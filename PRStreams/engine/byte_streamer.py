import asyncio
import logging
from typing import Dict

from pyrogram import Client, raw, utils
from pyrogram.errors import AuthBytesInvalid
from pyrogram.file_id import FileId, FileType, ThumbnailSource
from pyrogram.session import Auth, Session

from .file_properties import get_file_ids
from ..bot import work_loads
from ..vars import Var

logger = logging.getLogger("byte_streamer")


class ByteStreamer:
    """Streams file bytes straight from Telegram's DC with aggressive caching.

    Two caches make this fast:
      * ``cached_file_ids`` - avoids re-fetching the message/FileId per request.
      * ``client.media_sessions`` - reuses the authorized DC connection, so
        subsequent range requests skip the auth handshake entirely.
    """

    def __init__(self, client: Client):
        self.client = client
        self.clean_timer = 30 * 60
        self.cached_file_ids: Dict[int, FileId] = {}
        asyncio.create_task(self._clean_cache())

    async def get_file_properties(self, message_id: int) -> FileId:
        if message_id not in self.cached_file_ids:
            file_id = await get_file_ids(self.client, Var.STORAGE_CHANNEL, message_id)
            self.cached_file_ids[message_id] = file_id
        return self.cached_file_ids[message_id]

    async def _generate_media_session(self, client: Client, file_id: FileId) -> Session:
        media_session = client.media_sessions.get(file_id.dc_id, None)
        if media_session is not None:
            return media_session

        if file_id.dc_id != await client.storage.dc_id():
            media_session = Session(
                client,
                file_id.dc_id,
                await Auth(client, file_id.dc_id, await client.storage.test_mode()).create(),
                await client.storage.test_mode(),
                is_media=True,
            )
            await media_session.start()

            for _ in range(6):
                exported_auth = await client.invoke(
                    raw.functions.auth.ExportAuthorization(dc_id=file_id.dc_id)
                )
                try:
                    await media_session.invoke(
                        raw.functions.auth.ImportAuthorization(
                            id=exported_auth.id, bytes=exported_auth.bytes
                        )
                    )
                    break
                except AuthBytesInvalid:
                    continue
            else:
                await media_session.stop()
                raise AuthBytesInvalid
        else:
            media_session = Session(
                client,
                file_id.dc_id,
                await client.storage.auth_key(),
                await client.storage.test_mode(),
                is_media=True,
            )
            await media_session.start()

        client.media_sessions[file_id.dc_id] = media_session
        return media_session

    @staticmethod
    async def _get_location(file_id: FileId):
        file_type = file_id.file_type
        if file_type == FileType.CHAT_PHOTO:
            if file_id.chat_id > 0:
                peer = raw.types.InputPeerUser(
                    user_id=file_id.chat_id, access_hash=file_id.chat_access_hash
                )
            elif file_id.chat_access_hash == 0:
                peer = raw.types.InputPeerChat(chat_id=-file_id.chat_id)
            else:
                peer = raw.types.InputPeerChannel(
                    channel_id=utils.get_channel_id(file_id.chat_id),
                    access_hash=file_id.chat_access_hash,
                )
            return raw.types.InputPeerPhotoFileLocation(
                peer=peer,
                volume_id=file_id.volume_id,
                local_id=file_id.local_id,
                big=file_id.thumbnail_source == ThumbnailSource.CHAT_PHOTO_BIG,
            )
        if file_type == FileType.PHOTO:
            return raw.types.InputPhotoFileLocation(
                id=file_id.media_id,
                access_hash=file_id.access_hash,
                file_reference=file_id.file_reference,
                thumb_size=file_id.thumbnail_size,
            )
        return raw.types.InputDocumentFileLocation(
            id=file_id.media_id,
            access_hash=file_id.access_hash,
            file_reference=file_id.file_reference,
            thumb_size=file_id.thumbnail_size,
        )

    async def yield_file(
        self,
        file_id: FileId,
        index: int,
        offset: int,
        first_part_cut: int,
        last_part_cut: int,
        part_count: int,
        chunk_size: int,
    ):
        """Async generator yielding exactly the bytes of the requested range."""
        client = self.client
        work_loads[index] += 1
        try:
            media_session = await self._generate_media_session(client, file_id)
            location = await self._get_location(file_id)

            current_part = 1
            response = await media_session.invoke(
                raw.functions.upload.GetFile(
                    location=location, offset=offset, limit=chunk_size
                )
            )
            if not isinstance(response, raw.types.upload.File):
                return

            while current_part <= part_count:
                chunk = response.bytes
                if not chunk:
                    break
                if part_count == 1:
                    yield chunk[first_part_cut:last_part_cut]
                elif current_part == 1:
                    yield chunk[first_part_cut:]
                elif current_part == part_count:
                    yield chunk[:last_part_cut]
                else:
                    yield chunk

                current_part += 1
                offset += chunk_size
                if current_part > part_count:
                    break
                response = await media_session.invoke(
                    raw.functions.upload.GetFile(
                        location=location, offset=offset, limit=chunk_size
                    )
                )
        except (TimeoutError, ConnectionResetError, asyncio.CancelledError):
            # Player seeked away or the client disconnected mid-stream.
            pass
        finally:
            work_loads[index] -= 1

    async def _clean_cache(self):
        while True:
            await asyncio.sleep(self.clean_timer)
            self.cached_file_ids.clear()


# One ByteStreamer per underlying pyrogram client, shared across requests.
_streamers: Dict[Client, ByteStreamer] = {}


def get_byte_streamer(client: Client) -> ByteStreamer:
    streamer = _streamers.get(client)
    if streamer is None:
        streamer = ByteStreamer(client)
        _streamers[client] = streamer
    return streamer
