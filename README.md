# PR Streams — Telegram File → Link Bot (Streaming + Fast Downloads)

Send any file to the bot on Telegram and instantly get:

- ⬇️ a **high-speed direct download** link
- ▶️ a **beautiful streaming page** with a built-in player (light/dark toggle)
- 📲 one-tap **Open in VLC / MX Player** on both PC and Android
- ∞ **any file size** up to Telegram's own limit (2 GB, or **4 GB** from Premium accounts)
- 🎞️ **MKV, MP4, MOV, AVI, WEBM** and every popular format

It's built to fix the classic problem: *streaming is smooth but downloads are slow.*
See [Why downloads are fast here](#why-downloads-are-fast-here).

---

## Table of contents

1. [How it works](#how-it-works)
2. [Why downloads are fast here](#why-downloads-are-fast-here)
3. [Prerequisites](#prerequisites)
4. [Configuration reference](#configuration-reference)
5. [Deploy on a VPS (recommended)](#deploy-on-a-vps-recommended)
   - [Option A — Docker Compose](#option-a--docker-compose-easiest)
   - [Option B — systemd + nginx + HTTPS](#option-b--systemd--nginx--https-no-docker)
6. [Deploy with Docker anywhere](#deploy-with-docker-anywhere)
7. [Deploy on Koyeb / Render / Railway / Heroku](#deploy-on-a-paas)
8. [Multi-client speed & 4 GB files](#multi-client-speed--4-gb-files)
9. [Getting maximum download speed](#getting-maximum-download-speed)
10. [Using the bot](#using-the-bot)
11. [Troubleshooting](#troubleshooting)
12. [Project layout](#project-layout)

---

## How it works

1. You send (or forward) a file to the bot in a private chat.
2. The bot **copies** the message into a private **storage channel** (server-side —
   nothing is re-uploaded, so even a 4 GB file is instant).
3. It replies with a **stream link** and a **download link**, each carrying a short
   anti-scrape hash.
4. When someone opens a link, the web server **streams the file's bytes straight
   from Telegram's data centre in 1 MiB chunks**, honouring HTTP `Range` requests
   so seeking, resuming and multi-connection downloads all work.

Nothing is stored on the server's disk — it's a pure pass-through.

## Why downloads are fast here

If you've built these bots before, you've probably seen 4K streaming play
smoothly while a plain download crawls. That happens because a video player only
asks for **small byte ranges**, while a straight download pulls the **whole file
over a single Telegram connection**, which caps throughput.

PR Streams fixes it three ways:

- **Multi-client load balancing** — add extra bot tokens / user sessions and every
  request is served by the *least-busy* client, so downloads aren't stuck behind
  one connection. ([setup](#multi-client-speed--4-gb-files))
- **Cached media sessions** — the authorized DC connection is reused across
  requests, so range requests skip the handshake entirely.
- **First-class HTTP `Range` support** — this is what lets **download managers
  (IDM, aria2, ADM, 1DM) pull with 8–16 parallel connections**, which multiplies
  real-world speed. ([how](#getting-maximum-download-speed))

And because you host it on a **VPS**, there's no PaaS egress throttle in the way.

## Prerequisites

You need four things before deploying:

| # | What | Where to get it |
|---|------|-----------------|
| 1 | **API_ID** and **API_HASH** | <https://my.telegram.org> → *API development tools* |
| 2 | **BOT_TOKEN** | [@BotFather](https://t.me/BotFather) → `/newbot` |
| 3 | **Storage channel** | Create a **private channel**, add your bot as **admin**, and get its id (it starts with `-100…`). Forward any post from it to [@userinfobot](https://t.me/userinfobot) to read the id. |
| 4 | A **domain or public IP** | For a VPS, point a domain's A-record at the server (needed for HTTPS). |

> The bot must be an **admin** in the storage channel, otherwise it can't save or
> serve files.

## Configuration reference

Copy `config.env.sample` to `config.env` and fill it in (on a PaaS, set these as
environment variables instead).

| Variable | Required | Description |
|----------|:---:|-------------|
| `API_ID` | ✅ | From my.telegram.org |
| `API_HASH` | ✅ | From my.telegram.org |
| `BOT_TOKEN` | ✅ | From @BotFather |
| `STORAGE_CHANNEL` | ✅ | Private channel id (`-100…`) where the bot is admin |
| `FQDN` | ✅ | Public hostname/IP the links point to (no `http://`, no trailing `/`) |
| `HAS_SSL` | ▲ | `true` if the public URL is HTTPS (default `false`) |
| `NO_PORT` | ▲ | `true` when a reverse proxy serves on 80/443 so links omit `:8080` |
| `BIND_ADDRESS` | | Interface to bind (default `0.0.0.0`) |
| `PORT` | | Internal web port (default `8080`) |
| `OWNER_ID` | | Space/comma separated owner user ids (for `/status`) |
| `ALLOWED_USERS` | | If set, only these ids (+ owners) may create links; empty = everyone |
| `MULTI_TOKEN1…N` | | Extra bot tokens for faster downloads (all must be channel admins) |
| `USER_SESSION1…N` | | User session strings (Premium account ⇒ 4 GB files) |
| `WORKERS` | | Pyrogram worker threads (default `8`) |
| `HASH_LENGTH` | | Length of the link hash (default `6`, min `4`) |
| `PING_INTERVAL` | | Self-ping seconds to keep sleepy PaaS awake; keep `0` on a VPS |
| `NAME` | | Display name (default `PR Streams`) |

---

## Deploy on a VPS (recommended)

A VPS gives you the bandwidth and CPU that make downloads genuinely fast. Two
ways — pick one.

### Option A — Docker Compose (easiest)

```bash
# 1. Install Docker (Debian/Ubuntu)
curl -fsSL https://get.docker.com | sh

# 2. Get the code
git clone <your-repo-url> pr-streams && cd pr-streams

# 3. Configure
cp config.env.sample config.env
nano config.env          # fill in the values

# 4. Run
docker compose up -d --build

# Logs
docker compose logs -f
```

To put it behind HTTPS on a domain, run the nginx step from Option B (the proxy
config in `deploy/nginx.conf` points at `127.0.0.1:8080`, which is what compose
exposes). Set `HAS_SSL=true` and `NO_PORT=true` in `config.env`, then
`docker compose up -d` again.

### Option B — systemd + nginx + HTTPS (no Docker)

This is the classic long-running production setup.

```bash
# 1. System packages
sudo apt update && sudo apt install -y python3 python3-venv git nginx

# 2. Get the code
sudo git clone <your-repo-url> /opt/pr-streams
cd /opt/pr-streams

# 3. Python env + deps
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# 4. Configure
cp config.env.sample config.env
nano config.env
#   FQDN=your.domain.com
#   HAS_SSL=true
#   NO_PORT=true

# 5. Install the service
sudo cp deploy/prstreams.service /etc/systemd/system/prstreams.service
sudo systemctl daemon-reload
sudo systemctl enable --now prstreams
journalctl -u prstreams -f          # watch it start

# 6. nginx reverse proxy
sudo cp deploy/nginx.conf /etc/nginx/sites-available/prstreams
#   edit the file and replace  your.domain.com
sudo ln -s /etc/nginx/sites-available/prstreams /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 7. Free HTTPS certificate
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your.domain.com
```

`deploy/nginx.conf` already disables proxy buffering and removes size/time limits,
which is essential for large, fast streaming downloads. After certbot finishes,
your links will be `https://your.domain.com/...`.

To update later:

```bash
cd /opt/pr-streams && git pull
./venv/bin/pip install -r requirements.txt
sudo systemctl restart prstreams
```

---

## Deploy with Docker anywhere

```bash
docker build -t pr-streams .
docker run -d --name pr-streams --restart unless-stopped \
  --env-file config.env -p 8080:8080 pr-streams
```

Or point `docker-compose.yml` at any host with Docker installed.

---

## Deploy on a PaaS

These are handy for testing, but note that **free tiers throttle bandwidth**, so
downloads will be slower than on a VPS. Set `PING_INTERVAL=600` to keep free
dynos awake.

**Koyeb / Render / Railway**

1. Fork/push this repo to GitHub.
2. Create a new **Web Service** from the repo (they auto-detect the `Dockerfile`).
3. Add the environment variables from the [config reference](#configuration-reference).
4. Set `FQDN` to the app's public hostname, `HAS_SSL=true`, `NO_PORT=true`.
5. Deploy. The platform provides HTTPS automatically.

**Heroku**

```bash
heroku create your-app-name
heroku stack:set container            # uses the Dockerfile
# set config vars (or use app.json's one-click deploy button):
heroku config:set API_ID=... API_HASH=... BOT_TOKEN=... STORAGE_CHANNEL=... \
  FQDN=your-app-name.herokuapp.com HAS_SSL=true NO_PORT=true PING_INTERVAL=600
git push heroku HEAD:main
```

`app.json` is included for Heroku's one-click "Deploy" flow.

---

## Multi-client speed & 4 GB files

The single biggest speed upgrade is adding more clients so downloads spread out.

**More bot tokens (recommended):**

1. Create extra bots with @BotFather (as many as you like).
2. Add **every** one of them as an **admin** to your storage channel.
3. Put their tokens in `config.env`:
   ```env
   MULTI_TOKEN1=1111:AAA...
   MULTI_TOKEN2=2222:BBB...
   MULTI_TOKEN3=3333:CCC...
   ```
4. Restart. The logs will say `Multi-client mode active with N clients.`

**User sessions (also enables 4 GB files):**

Bot tokens can serve files up to 2 GB. To serve **4 GB** files uploaded by a
Telegram **Premium** account, add a user session from such an account:

```bash
pip install pyrofork TgCrypto-pyrofork
python generate_session.py          # run locally, paste in API_ID/HASH, log in
```

Put the printed string in `config.env`:

```env
USER_SESSION1=<the long string>
```

> Keep session strings secret — they grant full access to that account. The
> account should also be a member/admin of the storage channel.

There is **no artificial size cap** in PR Streams — anything Telegram lets the
bot access can be streamed and downloaded. Telegram's own hard limit is 2 GB
(normal) / 4 GB (Premium) per file.

## Getting maximum download speed

- **Use a download manager.** Because every link supports HTTP `Range`, tools
  like **IDM**, **aria2** (`aria2c -x16 -s16 "<link>"`), **1DM/ADM** (Android)
  download in 8–16 parallel streams — often several times faster than a browser's
  single-stream download.
- **Add more `MULTI_TOKEN`s** so those parallel connections land on different
  clients.
- **Host on a VPS with good bandwidth** (this repo's main assumption).
- Keep the reverse proxy config from `deploy/nginx.conf` (buffering off) so bytes
  flow straight through.

## Using the bot

1. Open your bot in Telegram and send `/start`.
2. Send or forward any file.
3. Tap **▶️ Stream / Watch** for the player page, or **⬇️ Download** for the link.
4. On the player page:
   - Watch in-browser (works for MP4/WebM and many MKVs).
   - If the browser can't decode it (common for MKV/HEVC), use **Open in VLC /
     MX Player** — buttons adapt to Android, iOS, Windows and macOS.
   - **Copy direct link** to paste into a download manager or desktop VLC
     (*Media → Open Network Stream*), or grab the **.m3u playlist**.
   - Toggle **light/dark** with the button in the top-right.

Bot commands: `/start`, `/help`, `/status` (owner).

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Bot replies with a storage error | Make sure the bot (and all `MULTI_TOKEN` bots) are **admins** in `STORAGE_CHANNEL`, and the id starts with `-100`. |
| Links open but 403 *invalid hash* | The `?hash=` was altered/truncated. Use the full link the bot sent. |
| Links point to `http://0.0.0.0:8080` | Set `FQDN`, `HAS_SSL`, `NO_PORT` correctly and restart. |
| MKV won't play in browser | Expected for some codecs — use the VLC / MX Player buttons. |
| Downloads still slow | Add `MULTI_TOKEN`s, use a download manager, and confirm you're on a VPS (not a throttled free tier) with the nginx buffering-off config. |
| Video won't seek | Ensure your proxy passes the `Range` header (the provided `nginx.conf` does). |

## Project layout

```
PRStreams/
  __main__.py            # boot: start client pool + web server
  vars.py                # configuration
  bot/
    __init__.py          # StreamBot + client pool globals
    clients.py           # start extra tokens / sessions
    plugins/             # /start, file handler, /status
  engine/
    byte_streamer.py     # CORE fast chunked streamer (cached sessions)
    file_properties.py   # resolve file id / name / size / hash
  server/
    stream_routes.py     # /, /watch, /dl, /m3u, /status routes + Range logic
  template/
    watch.html           # the stream page (player + VLC/MX + theme toggle)
    home.html
  utils/                 # helpers + HTML rendering
deploy/                  # nginx.conf, systemd unit
Dockerfile, docker-compose.yml, Procfile, app.json
config.env.sample, generate_session.py
```

---

Built with [Pyrofork](https://pypi.org/project/pyrofork/) + aiohttp.
