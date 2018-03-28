import asyncio

import aiohttp
from aiohttp import web


def hello(request):
    return web.Response(text='hello world')


app = web.Application()
app.add_routes([web.get('/', hello)])
web.run_app(app)
