from pyrogram import Client

from ..vars import Var

# Primary client. It handles Telegram updates (incoming files, commands) AND
# doubles as client index 0 in the download/stream load-balancing pool.
StreamBot = Client(
    name="PRStreams",
    api_id=Var.API_ID,
    api_hash=Var.API_HASH,
    bot_token=Var.BOT_TOKEN,
    sleep_threshold=Var.SLEEP_THRESHOLD,
    workers=Var.WORKERS,
    plugins={"root": "PRStreams/bot/plugins"},
    in_memory=True,
)

# index -> pyrogram Client   (0 is always StreamBot)
multi_clients = {}
# index -> number of in-flight transfers, used to pick the least busy client
work_loads = {}
