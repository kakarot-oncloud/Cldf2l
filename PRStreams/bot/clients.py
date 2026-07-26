import asyncio
import logging

from pyrogram import Client

from ..vars import Var
from . import StreamBot, multi_clients, work_loads

logger = logging.getLogger("clients")


async def initialize_clients():
    """Start every extra bot token / user session and register it in the
    load-balancing pool. Index 0 is always the primary StreamBot."""
    multi_clients[0] = StreamBot
    work_loads[0] = 0

    if not Var.MULTI_TOKENS and not Var.USER_SESSIONS:
        logger.info("No MULTI_TOKEN / USER_SESSION set -> running single-client mode.")
        return

    async def start_client(client_id: int, *, token: str = None, session: str = None):
        try:
            if session:
                client = Client(
                    name=f"user_{client_id}",
                    api_id=Var.API_ID,
                    api_hash=Var.API_HASH,
                    session_string=session,
                    sleep_threshold=Var.SLEEP_THRESHOLD,
                    no_updates=True,
                    in_memory=True,
                )
            else:
                client = Client(
                    name=f"bot_{client_id}",
                    api_id=Var.API_ID,
                    api_hash=Var.API_HASH,
                    bot_token=token,
                    sleep_threshold=Var.SLEEP_THRESHOLD,
                    no_updates=True,
                    in_memory=True,
                )
            await client.start()
            work_loads[client_id] = 0
            logger.info("Started helper client #%s", client_id)
            return client_id, client
        except Exception as exc:  # noqa: BLE001 - one bad token must not kill the rest
            logger.error("Failed to start client #%s: %s", client_id, exc)
            return None

    tasks = []
    next_id = 1
    for token in Var.MULTI_TOKENS:
        tasks.append(start_client(next_id, token=token))
        next_id += 1
    for session in Var.USER_SESSIONS:
        tasks.append(start_client(next_id, session=session))
        next_id += 1

    for result in await asyncio.gather(*tasks):
        if result:
            cid, client = result
            multi_clients[cid] = client

    if len(multi_clients) > 1:
        Var.MULTI_CLIENT = True
        logger.info("Multi-client mode active with %s clients.", len(multi_clients))
