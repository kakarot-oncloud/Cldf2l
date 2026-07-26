import os

from dotenv import load_dotenv

# Load config.env if it exists (VPS / bare-metal). On PaaS the values usually
# come straight from real environment variables, which os.environ already sees.
load_dotenv("config.env", override=False)


def _get_bool(name: str, default: bool) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in (
        "1",
        "true",
        "yes",
        "y",
        "on",
    )


def _get_int_set(name: str):
    return {int(x) for x in os.environ.get(name, "").replace(",", " ").split() if x.strip()}


def _collect(prefix: str):
    """Collect every env var that starts with ``prefix`` (e.g. MULTI_TOKEN1,
    MULTI_TOKEN2 ...) sorted by name so ordering is stable."""
    items = [(k, v) for k, v in os.environ.items() if k.startswith(prefix) and v.strip()]
    items.sort(key=lambda kv: kv[0])
    return [v for _, v in items]


class Var:
    # ---- Telegram credentials -------------------------------------------
    API_ID = int(os.environ.get("API_ID", "0"))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

    # Private channel/group where every incoming file is stored so it can be
    # served later. The bot MUST be an admin here. Example: -1001234567890
    STORAGE_CHANNEL = int(os.environ.get("STORAGE_CHANNEL", os.environ.get("BIN_CHANNEL", "0")))

    # ---- Ownership / access ---------------------------------------------
    OWNER_ID = _get_int_set("OWNER_ID")
    # If empty -> everyone may upload. Otherwise only these user ids (+ owners).
    ALLOWED_USERS = _get_int_set("ALLOWED_USERS")

    # ---- Web server -----------------------------------------------------
    BIND_ADDRESS = os.environ.get("BIND_ADDRESS", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "8080"))
    # Public hostname/IP the links should point to (no scheme, no trailing /).
    FQDN = os.environ.get("FQDN", "").strip() or BIND_ADDRESS
    HAS_SSL = _get_bool("HAS_SSL", False)
    # When True the public URL omits the :PORT part (typical behind nginx/443).
    NO_PORT = _get_bool("NO_PORT", False)

    _protocol = "https" if HAS_SSL else "http"
    if NO_PORT:
        URL = f"{_protocol}://{FQDN}/"
    else:
        URL = f"{_protocol}://{FQDN}:{PORT}/"

    # ---- Performance / multi-client -------------------------------------
    WORKERS = int(os.environ.get("WORKERS", "8"))
    SLEEP_THRESHOLD = int(os.environ.get("SLEEP_THRESHOLD", "60"))
    # Extra bot tokens (MULTI_TOKEN1, MULTI_TOKEN2, ...) and user session
    # strings (USER_SESSION1, ...) used for download/stream load balancing.
    MULTI_TOKENS = _collect("MULTI_TOKEN")
    USER_SESSIONS = _collect("USER_SESSION")
    MULTI_CLIENT = False  # flipped on at runtime when >1 client is live

    # ---- Misc -----------------------------------------------------------
    # Length of the anti-scrape hash appended to every link.
    HASH_LENGTH = max(4, int(os.environ.get("HASH_LENGTH", "6")))
    # Self-ping interval in seconds to keep sleepy PaaS dynos awake. 0 disables
    # it (recommended on a VPS).
    PING_INTERVAL = int(os.environ.get("PING_INTERVAL", "0"))
    NAME = os.environ.get("NAME", "PR Streams")
