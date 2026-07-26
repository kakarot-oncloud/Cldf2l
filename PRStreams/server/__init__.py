from aiohttp import web

from .stream_routes import routes


def web_server():
    # client_max_size is only relevant for uploads to us; keep it generous so
    # HEAD/GET with odd bodies never trips a limit. Downloads are unbounded.
    web_app = web.Application(client_max_size=30 * 1024 * 1024 * 1024)
    web_app.add_routes(routes)
    return web_app
