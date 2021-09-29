import logging
from aiohttp import web
import os
import sys

app = web.Application()
logging.basicConfig(level=logging.DEBUG)

routes = web.RouteTableDef()

if os.getenv('CONTENT_FOLDER'):
    routes.static('/', os.getenv('CONTENT_FOLDER'))
else:
    routes.static('/', sys.argv[1])

app.add_routes(routes)

if __name__ == '__main__':
    web.run_app(app=app, host='0.0.0.0', port=8000)
