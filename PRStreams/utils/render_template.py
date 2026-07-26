import html
import os
import urllib.parse

import aiofiles

from ..bot import multi_clients, work_loads
from ..engine.byte_streamer import get_byte_streamer
from ..exceptions import InvalidHash
from ..utils.human_readable import humanbytes
from ..vars import Var

_TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "template")


def _abs_url(path: str) -> str:
    return urllib.parse.urljoin(Var.URL, path)


async def _read_template(name: str) -> str:
    async with aiofiles.open(os.path.join(_TEMPLATE_DIR, name), mode="r", encoding="utf-8") as f:
        return await f.read()


async def render_watch_page(message_id: int, secure_hash: str) -> str:
    index = min(work_loads, key=work_loads.get)
    client = multi_clients[index]
    streamer = get_byte_streamer(client)

    file_id = await streamer.get_file_properties(message_id)
    if file_id.unique_id[: Var.HASH_LENGTH] != secure_hash:
        raise InvalidHash

    file_name = file_id.file_name
    quoted_name = urllib.parse.quote(file_name)
    mime_type = file_id.mime_type or "application/octet-stream"
    media_kind = mime_type.split("/")[0]  # video / audio / image / ...

    stream_url = _abs_url(f"dl/{message_id}/{quoted_name}?hash={secure_hash}")
    download_url = stream_url + "&download=1"
    m3u_url = _abs_url(f"m3u/{message_id}?hash={secure_hash}")

    template = await _read_template("watch.html")
    replacements = {
        "{{FILE_NAME}}": html.escape(file_name),
        "{{FILE_SIZE}}": html.escape(humanbytes(file_id.file_size)),
        "{{MIME_TYPE}}": html.escape(mime_type),
        "{{MEDIA_KIND}}": html.escape(media_kind),
        "{{STREAM_URL}}": html.escape(stream_url),
        "{{DOWNLOAD_URL}}": html.escape(download_url),
        "{{M3U_URL}}": html.escape(m3u_url),
        "{{BOT_NAME}}": html.escape(Var.NAME),
    }
    for token, value in replacements.items():
        template = template.replace(token, value)
    return template


async def render_home_page() -> str:
    template = await _read_template("home.html")
    return template.replace("{{BOT_NAME}}", html.escape(Var.NAME))
