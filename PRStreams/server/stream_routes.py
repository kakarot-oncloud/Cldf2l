import logging
import math
import mimetypes
import time
import urllib.parse

from aiohttp import web

from .. import StartTime, __version__
from ..bot import multi_clients, work_loads
from ..engine.byte_streamer import get_byte_streamer
from ..utils.human_readable import get_readable_time
from ..utils.render_template import render_home_page, render_watch_page
from ..vars import Var
from ..exceptions import FileNotFound, InvalidHash

logger = logging.getLogger("routes")
routes = web.RouteTableDef()

CHUNK_SIZE = 1024 * 1024  # 1 MiB - the maximum Telegram allows per GetFile part


@routes.get("/status", allow_head=True)
async def status_handler(_request):
    return web.json_response(
        {
            "status": "running",
            "bot": Var.NAME,
            "version": __version__,
            "uptime": get_readable_time(time.time() - StartTime),
            "connected_clients": len(multi_clients),
            "multi_client": Var.MULTI_CLIENT,
            "loads": {f"client_{k}": v for k, v in sorted(work_loads.items())},
        }
    )


@routes.get("/", allow_head=True)
async def home_handler(_request):
    return web.Response(text=await render_home_page(), content_type="text/html")


@routes.get(r"/watch/{message_id:\d+}", allow_head=True)
async def watch_handler(request: web.Request):
    try:
        message_id = int(request.match_info["message_id"])
        secure_hash = request.rel_url.query.get("hash", "")
        page = await render_watch_page(message_id, secure_hash)
        return web.Response(text=page, content_type="text/html")
    except InvalidHash as exc:
        raise web.HTTPForbidden(text=exc.message)
    except FileNotFound as exc:
        raise web.HTTPNotFound(text=exc.message)
    except Exception as exc:  # noqa: BLE001
        logger.critical("watch error: %s", exc, exc_info=True)
        raise web.HTTPInternalServerError(text=str(exc))


@routes.get(r"/m3u/{message_id:\d+}", allow_head=True)
async def m3u_handler(request: web.Request):
    """Return an .m3u playlist so desktop players (VLC/PotPlayer/MPV) can open
    the stream directly with one click."""
    try:
        message_id = int(request.match_info["message_id"])
        secure_hash = request.rel_url.query.get("hash", "")

        index = min(work_loads, key=work_loads.get)
        streamer = get_byte_streamer(multi_clients[index])
        file_id = await streamer.get_file_properties(message_id)
        if file_id.unique_id[: Var.HASH_LENGTH] != secure_hash:
            raise InvalidHash

        file_name = file_id.file_name
        quoted = urllib.parse.quote(file_name)
        direct = urllib.parse.urljoin(Var.URL, f"dl/{message_id}/{quoted}?hash={secure_hash}")
        playlist = f"#EXTM3U\n#EXTINF:-1,{file_name}\n{direct}\n"
        return web.Response(
            text=playlist,
            content_type="audio/x-mpegurl",
            headers={"Content-Disposition": f'attachment; filename="{file_name}.m3u"'},
        )
    except InvalidHash as exc:
        raise web.HTTPForbidden(text=exc.message)
    except FileNotFound as exc:
        raise web.HTTPNotFound(text=exc.message)


@routes.get(r"/dl/{message_id:\d+}", allow_head=True)
@routes.get(r"/dl/{message_id:\d+}/{file_name}", allow_head=True)
async def download_handler(request: web.Request):
    try:
        message_id = int(request.match_info["message_id"])
        secure_hash = request.rel_url.query.get("hash", "")
        return await media_streamer(request, message_id, secure_hash)
    except InvalidHash as exc:
        raise web.HTTPForbidden(text=exc.message)
    except FileNotFound as exc:
        raise web.HTTPNotFound(text=exc.message)
    except (ConnectionResetError, ConnectionAbortedError):
        return web.Response(status=499, text="Client closed the connection.")
    except Exception as exc:  # noqa: BLE001
        logger.critical("download error: %s", exc, exc_info=True)
        raise web.HTTPInternalServerError(text=str(exc))


async def media_streamer(request: web.Request, message_id: int, secure_hash: str):
    range_header = request.headers.get("Range", "")

    # Pick the least busy client so downloads spread across every token/session.
    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]
    if Var.MULTI_CLIENT:
        logger.info("Client #%s serving %s", index, request.remote)

    streamer = get_byte_streamer(faster_client)
    file_id = await streamer.get_file_properties(message_id)

    if file_id.unique_id[: Var.HASH_LENGTH] != secure_hash:
        raise InvalidHash

    file_size = file_id.file_size

    if range_header:
        raw_from, _, raw_to = range_header.replace("bytes=", "").partition("-")
        from_bytes = int(raw_from) if raw_from else 0
        until_bytes = int(raw_to) if raw_to else file_size - 1
    else:
        from_bytes = 0
        until_bytes = file_size - 1

    if until_bytes >= file_size:
        until_bytes = file_size - 1
    if (from_bytes < 0) or (from_bytes > until_bytes) or (from_bytes >= file_size):
        return web.Response(
            status=416,
            text="Requested Range Not Satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    offset = from_bytes - (from_bytes % CHUNK_SIZE)
    first_part_cut = from_bytes - offset
    last_part_cut = (until_bytes % CHUNK_SIZE) + 1
    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil(until_bytes / CHUNK_SIZE) - math.floor(offset / CHUNK_SIZE)

    mime_type = file_id.mime_type or mimetypes.guess_type(file_id.file_name)[0] or "application/octet-stream"
    file_name = file_id.file_name
    disposition = "attachment" if request.query.get("download") else "inline"
    # Sanitize for the plain filename token; keep the full name in filename* (RFC 5987).
    safe_name = file_name.replace('"', "").replace("\n", "").replace("\r", "")
    encoded_name = urllib.parse.quote(file_name)

    body = streamer.yield_file(
        file_id, index, offset, first_part_cut, last_part_cut, part_count, CHUNK_SIZE
    )

    headers = {
        "Content-Type": mime_type,
        "Content-Length": str(req_length),
        "Content-Disposition": f"{disposition}; filename=\"{safe_name}\"; filename*=UTF-8''{encoded_name}",
        "Accept-Ranges": "bytes",
        "Cache-Control": "public, max-age=604800",
    }
    if range_header:
        headers["Content-Range"] = f"bytes {from_bytes}-{until_bytes}/{file_size}"

    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers=headers,
    )
