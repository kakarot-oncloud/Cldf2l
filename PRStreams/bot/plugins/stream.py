import asyncio
import logging
import urllib.parse

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from PRStreams.engine.file_properties import get_hash, get_media_file_size, get_name
from PRStreams.utils.human_readable import humanbytes
from PRStreams.vars import Var

logger = logging.getLogger("stream")

MEDIA_FILTER = (
    filters.document
    | filters.video
    | filters.audio
    | filters.animation
    | filters.voice
    | filters.video_note
    | filters.photo
)


def _is_authorized(message: Message) -> bool:
    if not Var.ALLOWED_USERS:
        return True
    if not message.from_user:
        return False
    uid = message.from_user.id
    return uid in Var.ALLOWED_USERS or uid in Var.OWNER_ID


@Client.on_message(filters.private & MEDIA_FILTER, group=4)
async def media_receive_handler(_client: Client, message: Message):
    if not _is_authorized(message):
        await message.reply_text(
            "🚫 You are not authorized to use this bot.", quote=True
        )
        return

    try:
        stored = await message.copy(chat_id=Var.STORAGE_CHANNEL)
    except FloodWait as exc:
        logger.warning("FloodWait: sleeping %s seconds", exc.value)
        await asyncio.sleep(exc.value)
        stored = await message.copy(chat_id=Var.STORAGE_CHANNEL)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to store file: %s", exc, exc_info=True)
        await message.reply_text(
            "❌ Couldn't process this file. Make sure the bot is an admin in the "
            "storage channel and try again.",
            quote=True,
        )
        return

    file_name = get_name(stored)
    file_size = humanbytes(get_media_file_size(stored))
    file_hash = get_hash(stored, Var.HASH_LENGTH)

    quoted = urllib.parse.quote(file_name)
    stream_link = f"{Var.URL}watch/{stored.id}?hash={file_hash}"
    download_link = f"{Var.URL}dl/{stored.id}/{quoted}?hash={file_hash}"

    text = (
        "**✅ Your links are ready!**\n\n"
        f"**📁 Name:** `{file_name}`\n"
        f"**📦 Size:** {file_size}\n\n"
        f"**▶️ Stream / Watch:**\n{stream_link}\n\n"
        f"**⬇️ Direct Download:**\n{download_link}\n\n"
        "_Tip: paste the download link into a download manager for maximum speed._"
    )

    await message.reply_text(
        text,
        quote=True,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("▶️ Stream / Watch", url=stream_link),
                    InlineKeyboardButton("⬇️ Download", url=download_link),
                ]
            ]
        ),
    )
