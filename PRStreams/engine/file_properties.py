from typing import Optional

from pyrogram import Client
from pyrogram.file_id import FileId
from pyrogram.types import Message

from ..vars import Var
from ..exceptions import FileNotFound

# Order matters: check the "richer" media types before generic ones.
_MEDIA_TYPES = (
    "document",
    "video",
    "audio",
    "animation",
    "voice",
    "video_note",
    "photo",
    "sticker",
)


def get_media_from_message(message: Message):
    for attr in _MEDIA_TYPES:
        media = getattr(message, attr, None)
        if media:
            return media
    return None


def get_media_file_size(message: Message) -> int:
    media = get_media_from_message(message)
    return int(getattr(media, "file_size", 0) or 0)


def get_media_mime(message: Message) -> str:
    media = get_media_from_message(message)
    return getattr(media, "mime_type", "") or ""


def get_name(message: Message) -> str:
    media = get_media_from_message(message)
    file_name = getattr(media, "file_name", "") if media else ""
    if file_name:
        return file_name

    # Fall back to a sensible synthetic name based on the media type.
    mid = message.id
    if getattr(message, "video", None):
        return f"video_{mid}.mp4"
    if getattr(message, "animation", None):
        return f"gif_{mid}.mp4"
    if getattr(message, "video_note", None):
        return f"videonote_{mid}.mp4"
    if getattr(message, "audio", None):
        return f"audio_{mid}.mp3"
    if getattr(message, "voice", None):
        return f"voice_{mid}.ogg"
    if getattr(message, "photo", None):
        return f"photo_{mid}.jpg"
    if getattr(message, "sticker", None):
        return f"sticker_{mid}.webp"
    return f"file_{mid}.bin"


def get_hash(message: Message, length: int = None) -> str:
    length = length or Var.HASH_LENGTH
    media = get_media_from_message(message)
    unique_id = getattr(media, "file_unique_id", "") if media else ""
    return unique_id[:length]


async def get_file_ids(client: Client, chat_id: int, message_id: int) -> Optional[FileId]:
    """Resolve a stored message into a decoded FileId enriched with the
    metadata the streamer/renderer needs (size, mime, name, unique id)."""
    message = await client.get_messages(chat_id, message_id)
    if not message or getattr(message, "empty", False):
        raise FileNotFound
    media = get_media_from_message(message)
    if not media:
        raise FileNotFound

    file_id = FileId.decode(media.file_id)
    setattr(file_id, "file_size", int(getattr(media, "file_size", 0) or 0))
    setattr(file_id, "mime_type", getattr(media, "mime_type", "") or "")
    setattr(file_id, "file_name", get_name(message))
    setattr(file_id, "unique_id", media.file_unique_id)
    return file_id
