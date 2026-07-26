import logging

from pyrogram import Client, ContinuePropagation
from pyrogram.types import Message

log = logging.getLogger("PRStreams")


# Runs first (very low group) for EVERY incoming message, logs it, then lets the
# real handlers run. Temporary diagnostic — safe to remove later.
@Client.on_message(group=-999)
async def _log_incoming(_client: Client, message: Message):
    try:
        kind = message.media.value if message.media else "text"
    except Exception:
        kind = "unknown"
    chat = getattr(message.chat, "id", None)
    user = getattr(message.from_user, "id", None)
    log.info("INCOMING update -> chat=%s user=%s kind=%s text=%r", chat, user, kind, getattr(message, "text", None))
    raise ContinuePropagation
