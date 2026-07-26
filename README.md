<div align="center">

# 🎬 PR Streams

### Telegram File → Link Bot · Streaming + High-Speed Downloads

Turn **any file** you send on Telegram into an instant **streaming page** and a
**fast direct download** link.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pyrofork](https://img.shields.io/badge/Pyrofork-MTProto-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![aiohttp](https://img.shields.io/badge/aiohttp-async-2C5BB4?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

</div>

---

**What you get:**

- ⬇️ a **fast direct download** link (works great with download managers)
- ▶️ a **nice video player page** with a **light / dark** switch
- 📲 one-tap **“Open in VLC / MX Player”** for phone and computer
- ∞ **any size** file — up to Telegram’s own limit (2 GB, or **4 GB** with Premium)
- 🎞️ plays **MKV, MP4, MOV, AVI, WEBM** and all popular formats

> 💡 This guide is written so **anyone** can set it up — even if you’ve never
> written a line of code. Just follow the steps and **copy-paste** the boxes. 🙂

---

## 🧭 Super simple overview

You only need to do **3 things**:

1. **Get your keys** (5 minutes of clicking — [Step 1](#-step-1-get-your-4-keys)).
2. **Put the bot online** using ONE of the methods in [Step 2](#-step-2-put-the-bot-online-pick-one).
3. **Send a file** to your bot and enjoy your links 🎉

---

## 🔑 Step 1: Get your 4 keys

Grab these 4 things and paste them into a notepad for later. Don’t share them with anyone.

### 1) API_ID and API_HASH
1. Open **https://my.telegram.org** in a browser.
2. Log in with your phone number (Telegram sends you a code).
3. Click **API development tools**.
4. Fill the form (App title: `PR Streams`, short name: `prstreams`, anything works).
5. Click **Create application**.
6. Copy the **App api_id** (a number) and **App api_hash** (a long code). ✅

### 2) BOT_TOKEN
1. Open Telegram and search for **@BotFather** (the one with a blue tick).
2. Send `/newbot`.
3. Give your bot a **name** (e.g. `PR Streams`) and a **username** ending in `bot`
   (e.g. `pr_streams_bot`).
4. BotFather sends you a **token** that looks like `123456:ABC-DEF...`. Copy it. ✅

### 3) STORAGE_CHANNEL (where files are kept)
1. In Telegram, tap the pencil ✏️ → **New Channel**. Make it **Private**.
2. Open the channel → **Administrators** → **Add Admin** → add **your bot**
   (search its username). Give it all permissions. ✅
3. Now find the channel’s **ID number**:
   - Post any message in the channel.
   - Forward that message to **@userinfobot**.
   - It replies with an id like `-1001234567890`. Copy it (keep the `-100`). ✅

### 4) A place to run it (host)
Pick this in Step 2 below. If you have a **VPS**, great. If you don’t, use the
free **Railway/Render** method — no computer skills needed.

---

## 🚀 Step 2: Put the bot online (pick ONE)

Pick the method that fits you. **You only need one.**

| Method | Best for | Difficulty |
|--------|----------|:---:|
| [A. Railway / Render (website)](#a--railway--render-easiest-no-commands) | Beginners, no VPS | ⭐ Easiest |
| [B. VPS with Docker](#b--vps-with-docker-copy-paste) | You have a VPS | ⭐⭐ Easy |
| [C. VPS without Docker](#c--vps-without-docker-copy-paste) | You have a VPS | ⭐⭐ Easy |
| [D. Heroku](#d--heroku) | Heroku users | ⭐⭐ Easy |

---

### A) 🌐 Railway / Render (easiest, no commands)

No computer skills needed — you just click buttons on a website.

**First, put this code on GitHub (one time):**
1. Make a free account at **https://github.com**.
2. Create a new empty repository (click **New**, give it a name, **Create**).
3. Upload these files: on the repo page click **Add file → Upload files**, drag in
   everything from this project, then **Commit changes**. (Or click **“Fork”** if
   you’re viewing this project on GitHub — even easier.)

**Then deploy on Railway (or Render — same idea):**
1. Go to **https://railway.app** and sign in with GitHub.
2. Click **New Project → Deploy from GitHub repo** and choose your repo.
3. It sees the `Dockerfile` and starts building. Wait for it.
4. Open the **Variables** tab and add these (from Step 1):

   ```
   API_ID = your number
   API_HASH = your hash
   BOT_TOKEN = your bot token
   STORAGE_CHANNEL = -1001234567890
   HAS_SSL = true
   NO_PORT = true
   PING_INTERVAL = 600
   ```
5. In **Settings → Networking**, click **Generate Domain**. Copy the domain it
   gives you (looks like `something.up.railway.app`).
6. Add one more variable:

   ```
   FQDN = something.up.railway.app
   ```
7. Click **Deploy / Redeploy**. Done! ✅

> **Render** is identical: New → **Web Service** → pick your repo → it detects the
> Dockerfile → add the same variables → set `FQDN` to the URL Render gives you.

Now jump to [Step 3: Use the bot](#-step-3-use-your-bot).

---

### B) 🐳 VPS with Docker (copy‑paste)

You have a VPS (Ubuntu/Debian). Log in to it (via SSH / the provider’s console),
then copy‑paste these boxes **one at a time**, pressing **Enter** after each.

**1. Install Docker** (copy the whole box):
```bash
curl -fsSL https://get.docker.com | sh
```

**2. Download the project and open its folder:**
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git pr-streams
cd pr-streams
```
> Replace the link with your GitHub repo link. Don’t have it on GitHub? Upload it
> there first (see method A), or ask however you got this project for the link.

**3. Create your settings file:**
```bash
cp config.env.sample config.env
nano config.env
```
A text editor opens. Fill in your 4 keys and your domain, like this:
```env
API_ID=12345678
API_HASH=your_api_hash
BOT_TOKEN=123456:ABC-DEF...
STORAGE_CHANNEL=-1001234567890
FQDN=your.domain.com
HAS_SSL=true
NO_PORT=true
```
Save and exit nano: press **Ctrl+O**, then **Enter**, then **Ctrl+X**.

**4. Start the bot:**
```bash
docker compose up -d --build
```

**5. (See it working)**
```bash
docker compose logs -f
```
When you see `PR Streams is up!` it’s running. Press **Ctrl+C** to stop watching
the logs (the bot keeps running).

> **🎛️ Want a different port?** By default the bot uses **8080**. To use another
> port (for example `3359`), do these two things **before** step 4:
> 1. In `config.env`, set `PORT=3359`.
> 2. Run this one line so Docker uses the same port:
>    ```bash
>    sed -i 's/8080/3359/g' docker-compose.yml
>    ```
> Then continue with step 4. Your links will use that port
> (`http://your-address:3359/...`). If you use a firewall, open that port too.

> **🔄 Updating later (get new fixes):** from inside the `pr-streams` folder run:
> ```bash
> git pull && docker compose up -d --build
> ```
> If you only edited `config.env`, use `docker compose up -d --force-recreate`.

Now set up your domain + free HTTPS → see [Step 2.5](#-step-25-domain--free-https-for-vps-only).

---

### C) 🖥️ VPS without Docker (copy‑paste)

Prefer no Docker? Copy‑paste these on your Ubuntu/Debian VPS:

**1. Install the basics:**
```bash
sudo apt update && sudo apt install -y python3 python3-venv git nginx
```

**2. Get the project:**
```bash
sudo git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git /opt/pr-streams
cd /opt/pr-streams
```

**3. Install the bot’s parts:**
```bash
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
```

**4. Create your settings:**
```bash
cp config.env.sample config.env
nano config.env
```
Fill in your keys (same as method B), then **Ctrl+O**, **Enter**, **Ctrl+X**.

**5. Make it run 24/7 and start on boot:**
```bash
sudo cp deploy/prstreams.service /etc/systemd/system/prstreams.service
sudo systemctl daemon-reload
sudo systemctl enable --now prstreams
```

**6. Check it’s alive:**
```bash
journalctl -u prstreams -f
```
Press **Ctrl+C** to stop watching (bot keeps running).

Now set up your domain + free HTTPS → see [Step 2.5](#-step-25-domain--free-https-for-vps-only).

---

### D) 🟪 Heroku

```bash
heroku create your-app-name
heroku stack:set container
heroku config:set API_ID=12345678 API_HASH=your_hash BOT_TOKEN=123456:ABC \
  STORAGE_CHANNEL=-1001234567890 \
  FQDN=your-app-name.herokuapp.com HAS_SSL=true NO_PORT=true PING_INTERVAL=600
git push heroku HEAD:main
```
Heroku gives HTTPS automatically, so you can skip Step 2.5. Then go to
[Step 3](#-step-3-use-your-bot).

---

## 🔒 Step 2.5: Domain + free HTTPS (VPS only)

Do this only if you used method **B** or **C** and want a clean `https://` link
on your own domain.

**1. Point your domain at the server:** in your domain provider’s dashboard, add
an **A record** for `your.domain.com` pointing to your VPS’s IP address. Wait a
few minutes.

**2. Set up the web address (copy‑paste):**
```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/prstreams
sudo nano /etc/nginx/sites-available/prstreams
```
Change every `your.domain.com` to your real domain. Save (**Ctrl+O**, **Enter**,
**Ctrl+X**), then:
```bash
sudo ln -s /etc/nginx/sites-available/prstreams /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

**3. Get the free padlock (HTTPS):**
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your.domain.com
```
Follow the prompts (enter your email, agree). Done — your links are now
`https://your.domain.com/...` ✅

> Make sure your `config.env` has `FQDN=your.domain.com`, `HAS_SSL=true`,
> `NO_PORT=true`, then restart:
> - Docker: `docker compose up -d`
> - No‑Docker: `sudo systemctl restart prstreams`

---

## 📲 Step 3: Use your bot

1. Open your bot in Telegram and send **/start**.
2. **Send or forward any file** to it.
3. It replies with two buttons:
   - **▶️ Stream / Watch** — opens the player page.
   - **⬇️ Download** — the direct download link.
4. On the player page you can:
   - Watch right in the browser.
   - If a video won’t play (some MKV/HEVC don’t play in browsers), tap
     **Open in VLC / MX Player** — buttons appear for your device.
   - **Copy direct link** to paste into a download manager (fastest!) or into
     VLC on a PC (*Media → Open Network Stream*).
   - Flip **light/dark** with the button at the top‑right.

Bot commands: `/start`, `/help`, `/status` (owner only).

---

## ⚡ Make downloads even faster (optional)

The bot is already fast, but here’s how to push it further.

**Tip 1 — Use a download manager.** Because every link supports resuming and
splitting, apps like **IDM** (Windows), **1DM/ADM** (Android), or **aria2**
download in many pieces at once — often several times faster:
```bash
aria2c -x16 -s16 "PASTE_YOUR_DOWNLOAD_LINK_HERE"
```

**Tip 2 — Add extra bots (multi‑client).** This spreads downloads across several
connections. Create more bots with @BotFather, **add each one as admin** to your
storage channel, then add their tokens to `config.env`:
```env
MULTI_TOKEN1=1111:AAA...
MULTI_TOKEN2=2222:BBB...
MULTI_TOKEN3=3333:CCC...
```
Restart the bot. The logs will say `Multi-client mode active with N clients.`

**Tip 3 — Use a VPS with good bandwidth.** Free website hosts (Railway/Render
free tiers) limit speed; a VPS is faster.

---

## 🎞️ Big files & 4 GB support

There’s **no size limit added by this bot** — it serves whatever Telegram lets it.
Telegram’s own limits are **2 GB** per file for normal accounts and **4 GB** for
Telegram **Premium** accounts.

To serve **4 GB** files, add a Premium account’s “session” to the bot:
```bash
pip install pyrofork TgCrypto-pyrofork
python generate_session.py
```
It asks for your API_ID/API_HASH and logs you in, then prints a long string. Put
it in `config.env`:
```env
USER_SESSION1=the_long_string_it_printed
```
> Keep that string secret — it logs into that account. The account should be a
> member of your storage channel.

---

## 🆘 Troubleshooting

| Problem | Fix |
|--------|-----|
| Bot says it can’t save the file | Make sure the bot is an **admin** in your storage channel and the id starts with `-100`. |
| Link shows **“invalid hash”** | Use the *full* link the bot sent — don’t cut off the `?hash=` part. |
| Links look like `http://0.0.0.0:8080` | Set `FQDN`, `HAS_SSL`, `NO_PORT` correctly, then restart. |
| A video won’t play in the browser | Normal for some MKV/HEVC — use the **VLC / MX Player** buttons. |
| Downloads feel slow | Add `MULTI_TOKEN`s, use a download manager, and use a VPS (not a free tier). |
| Video won’t skip/seek | Your web setup must pass the `Range` header — the provided `deploy/nginx.conf` already does. |
| I changed `config.env` | Restart: `docker compose up -d` **or** `sudo systemctl restart prstreams`. |

---

## ⚙️ Settings reference (config.env)

| Variable | Needed? | What it is |
|----------|:---:|------------|
| `API_ID` | ✅ | From my.telegram.org |
| `API_HASH` | ✅ | From my.telegram.org |
| `BOT_TOKEN` | ✅ | From @BotFather |
| `STORAGE_CHANNEL` | ✅ | Private channel id (`-100…`), bot is admin |
| `FQDN` | ✅ | Your public address (no `http://`, no trailing `/`) |
| `HAS_SSL` | ▲ | `true` if the link is https |
| `NO_PORT` | ▲ | `true` when served on normal 80/443 (hides `:8080`) |
| `BIND_ADDRESS` | | Interface to bind (default `0.0.0.0`) |
| `PORT` | | Internal port (default `8080`) |
| `OWNER_ID` | | Your Telegram user id(s), space‑separated |
| `ALLOWED_USERS` | | If set, only these ids may make links; empty = everyone |
| `MULTI_TOKEN1…N` | | Extra bot tokens for speed (all channel admins) |
| `USER_SESSION1…N` | | User session strings (Premium ⇒ 4 GB files) |
| `WORKERS` | | Worker threads (default `8`) |
| `HASH_LENGTH` | | Link hash length (default `6`) |
| `PING_INTERVAL` | | Self‑ping seconds to keep free hosts awake; `0` on a VPS |
| `NAME` | | Display name (default `PR Streams`) |

---

## 🔧 How it works (for the curious)

1. You send a file → the bot **copies** it to your private storage channel
   (server‑side, so even 4 GB is instant — nothing is re‑uploaded).
2. It makes a stream link and a download link with a short anti‑scrape hash.
3. When a link is opened, the server **streams the file’s bytes straight from
   Telegram** in 1 MiB chunks and understands HTTP `Range`, so seeking, resuming,
   and multi‑connection download managers all work.

**Why downloads are fast here:** a plain download normally crawls because it uses
a single Telegram connection. PR Streams spreads requests across multiple clients
(your extra bot tokens), reuses authorized connections, and supports `Range` so
download managers pull many pieces in parallel. On a VPS there’s no host throttle
in the way.

## 🗂️ Project layout

```
PRStreams/
  __main__.py            # starts the bot + web server
  vars.py                # reads config.env
  bot/
    __init__.py          # the bot + client pool
    clients.py           # start extra tokens / sessions
    plugins/             # /start, file handler, /status
  engine/
    byte_streamer.py     # the fast chunked streamer
    file_properties.py   # file name / size / hash helpers
  server/
    stream_routes.py     # web routes + Range logic
  template/
    watch.html           # the player page (VLC/MX + light/dark)
    home.html
  utils/                 # helpers + HTML rendering
deploy/                  # nginx.conf, systemd service
Dockerfile, docker-compose.yml, Procfile, app.json
config.env.sample, generate_session.py
```

---

Built with [Pyrofork](https://pypi.org/project/pyrofork/) + aiohttp.
