"""Generate a Pyrogram user session string for USER_SESSION* (optional).

A user session lets PR Streams load-balance downloads across a real account and,
if that account has Telegram Premium, serve files up to 4 GB.

Run it locally (NOT on the server):

    pip install pyrofork TgCrypto-pyrofork
    python generate_session.py

Then paste the printed string into config.env as USER_SESSION1=...
Keep it secret — it grants full access to that account.
"""

from pyrogram import Client

api_id = int(input("API_ID: ").strip())
api_hash = input("API_HASH: ").strip()

with Client("pr_streams_session", api_id=api_id, api_hash=api_hash, in_memory=True) as app:
    session_string = app.export_session_string()
    print("\n================= YOUR SESSION STRING =================\n")
    print(session_string)
    print("\n======================================================")
    print("Add it to config.env as:  USER_SESSION1=<the string above>")
