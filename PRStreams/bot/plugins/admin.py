import time

from pyrogram import filters
from pyrogram.types import CallbackQuery, Message

from PRStreams import StartTime, __version__
from PRStreams.bot import StreamBot, multi_clients, work_loads
from PRStreams.utils.human_readable import get_readable_time
from PRStreams.vars import Var


def _status_text() -> str:
    uptime = get_readable_time(time.time() - StartTime)
    loads = "\n".join(
        f"   • client {k}: {v} active" for k, v in sorted(work_loads.items())
    )
    return (
        f"**📊 {Var.NAME} — status**\n\n"
        f"**Version:** `{__version__}`\n"
        f"**Uptime:** `{uptime}`\n"
        f"**Connected clients:** `{len(multi_clients)}`\n"
        f"**Multi-client:** `{Var.MULTI_CLIENT}`\n\n"
        f"**Work loads:**\n{loads}"
    )


@StreamBot.on_message(filters.command(["status", "stats"]) & filters.private)
async def status_command(_client, message: Message):
    if Var.OWNER_ID and (not message.from_user or message.from_user.id not in Var.OWNER_ID):
        return
    await message.reply_text(_status_text(), quote=True, disable_web_page_preview=True)


@StreamBot.on_callback_query(filters.regex("^status$"))
async def status_callback(_client, query: CallbackQuery):
    await query.answer()
    await query.message.reply_text(_status_text(), disable_web_page_preview=True)


@StreamBot.on_callback_query(filters.regex("^help$"))
async def help_callback(_client, query: CallbackQuery):
    from PRStreams.bot.plugins.start import HELP_TEXT

    await query.answer()
    await query.message.reply_text(
        HELP_TEXT.format(name=Var.NAME), disable_web_page_preview=True
    )
