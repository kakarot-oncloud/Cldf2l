def humanbytes(size) -> str:
    if not size:
        return "0 B"
    size = float(size)
    power = 1024
    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
    n = 0
    while size >= power and n < len(units) - 1:
        size /= power
        n += 1
    return f"{size:.2f} {units[n]}"


def get_readable_time(seconds: int) -> str:
    seconds = int(seconds)
    periods = [("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]
    parts = []
    for suffix, length in periods:
        if seconds >= length:
            value, seconds = divmod(seconds, length)
            parts.append(f"{value}{suffix}")
    return " ".join(parts) if parts else "0s"
