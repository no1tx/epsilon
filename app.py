import logging
from aiohttp import web
from aiohttp.abc import AbstractAccessLogger
import os
import sys
from re import search
from geolite2 import geolite2

geoip_match = geolite2.reader()

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger()

routes = web.RouteTableDef()

bad_useragent_chunks = [
    'bot', 'Bot', 'Crawler', 'crawl', 'Crawl',
]


class AccessLogger(AbstractAccessLogger):
    def log(self, request, response, time):
        if 'X-Real-IP' in request.headers:
            remote = request.headers['X-Real-IP']
        else:
            remote = request.remote
        geoip = geoip_match.get(remote)
        if geoip is not None:
            continent = geoip['continent']['code']
            country = geoip['country']['code']
            city = geoip['city']['names']['en']
        else:
            continent = 'N'
            country = 'N'
            city = 'N'
        if 'User-Agent' in request.headers:
            self.logger.info(f'{remote} {continent}:{country}:{city}'
                             f'{request.method} {request.path} '
                             f'done in {round(time, 2)}s: {response.status}. User Agent: {request.headers["User-Agent"]}')
        else:
            self.logger.info(f'{remote} {continent}:{country}:{city}'
                             f'{request.method} {request.path} '
                             f': detected a teapot without User-Agent header.')


@web.middleware
async def main_middleware(request, handler):
    if 'User-Agent' in request.headers:
        for _ in bad_useragent_chunks:
            if search(_, request.headers['User-Agent']):
                return web.Response(status=403, text="Go away motherfucker.")
    else:
        return web.Response(status=418, text="Who are you?")
    response = await handler(request)
    return response


if os.getenv('CONTENT_FOLDER'):
    routes.static('/', os.getenv('CONTENT_FOLDER'), show_index=True, follow_symlinks=True)
else:
    routes.static('/', sys.argv[2], show_index=True, follow_symlinks=True)

app = web.Application(middlewares=[main_middleware])

app.add_routes(routes)

if __name__ == '__main__':
    web.run_app(app=app, host='0.0.0.0', port=int(sys.argv[1]), access_log_class=AccessLogger)
