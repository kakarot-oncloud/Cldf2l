import asyncio

import aiohttp
from aiohttp import web
from pyrogram import idle

from . import LOGGER
from .bot import StreamBot
from .bot.clients import initialize_clients
from .server import web_server
from .vars import Var


async def _ping_loop():
    """Keep sleepy PaaS dynos awake. Disabled when PING_INTERVAL is 0 (VPS)."""
    while True:
        await asyncio.sleep(Var.PING_INTERVAL)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{Var.URL}status") as resp:
                    LOGGER.info("Self-ping -> %s", resp.status)
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("Self-ping failed: %s", exc)


async def start_services():
    LOGGER.info("------------------- Starting %s -------------------", Var.NAME)

    if not Var.API_ID or not Var.API_HASH or not Var.BOT_TOKEN:
        raise SystemExit("API_ID, API_HASH and BOT_TOKEN are required. Check config.env.")
    if not Var.STORAGE_CHANNEL:
        raise SystemExit("STORAGE_CHANNEL is required (the bot must be admin there).")

    await StreamBot.start()
    me = await StreamBot.get_me()
    StreamBot.username = me.username
    LOGGER.info("Bot online as @%s", me.username)

    await initialize_clients()

    app = web_server()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, Var.BIND_ADDRESS, Var.PORT)
    await site.start()
    LOGGER.info("Web server listening on %s:%s", Var.BIND_ADDRESS, Var.PORT)
    LOGGER.info("Public URL: %s", Var.URL)

    if Var.PING_INTERVAL > 0:
        asyncio.create_task(_ping_loop())

    LOGGER.info("------------------- %s is up! -------------------", Var.NAME)
    await idle()

    LOGGER.info("Shutting down...")
    await runner.cleanup()
    await StreamBot.stop()


if __name__ == "__main__":
    try:
        asyncio.run(start_services())
    except KeyboardInterrupt:
        LOGGER.info("Stopped by keyboard interrupt.")
