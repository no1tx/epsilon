import logging
from aiohttp import web
import os
import sys
from re import search

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger()

routes = web.RouteTableDef()

bad_useragent_chunks = [
    'bot', 'Bot', 'Crawler', 'crawl', 'Crawl',
]


@web.middleware
async def main_middleware(request, handler):
    for _ in bad_useragent_chunks:
        if search(_, request.headers['User-Agent']):
            return web.Response(status=403, text="Go away motherfucker.")
    response = await handler(request)
    return response


if os.getenv('CONTENT_FOLDER'):
    routes.static('/', os.getenv('CONTENT_FOLDER'), show_index=True, follow_symlinks=True)
else:
    routes.static('/', sys.argv[1], show_index=True, follow_symlinks=True)

app = web.Application(middlewares=[main_middleware])

app.add_routes(routes)

if __name__ == '__main__':
    web.run_app(app=app, host='0.0.0.0', port=8000)
