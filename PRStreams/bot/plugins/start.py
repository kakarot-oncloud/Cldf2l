from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from PRStreams.vars import Var

START_TEXT = (
    "**👋 Welcome to {name}!**\n\n"
    "Send or forward me **any file** — video, movie, document, audio, anything — "
    "and I'll instantly give you:\n\n"
    "• ⬇️ a **high-speed direct download** link\n"
    "• ▶️ a **streaming page** with a built-in player\n"
    "• 📲 one-tap **Open in VLC / MX Player** on PC & Android\n\n"
    "No size limits beyond Telegram's own (2 GB, or 4 GB from Premium accounts). "
    "MKV, MP4, MOV and every popular format are supported.\n\n"
    "Just drop a file to begin."
)

HELP_TEXT = (
    "**ℹ️ How to use {name}**\n\n"
    "1. Send or forward a file to this chat.\n"
    "2. Tap **Stream / Watch** to open the player page, or **Download** for the "
    "direct link.\n"
    "3. On the player page you can watch in-browser, or use **Open in VLC / "
    "MX Player** for MKV / HEVC and other formats.\n\n"
    "**Faster downloads:** paste the direct link into a download manager "
    "(IDM, ADM, aria2, 1DM). The links support multi-connection downloading, "
    "which multiplies your speed.\n\n"
    "**Commands**\n"
    "• /start – show the welcome message\n"
    "• /help – this help\n"
    "• /status – bot & server status"
)


def _buttons():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("❓ Help", callback_data="help"),
          InlineKeyboardButton("📊 Status", callback_data="status")]]
    )


@Client.on_message(filters.command("start") & filters.private)
async def start_command(_client: Client, message: Message):
    await message.reply_text(
        START_TEXT.format(name=Var.NAME),
        quote=True,
        disable_web_page_preview=True,
        reply_markup=_buttons(),
    )


@Client.on_message(filters.command(["help", "about"]) & filters.private)
async def help_command(_client: Client, message: Message):
    await message.reply_text(
        HELP_TEXT.format(name=Var.NAME),
        quote=True,
        disable_web_page_preview=True,
    )
