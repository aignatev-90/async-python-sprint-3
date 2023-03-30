import asyncio
import socket
from aiohttp import web


routes = web.RouteTableDef()

# def html_response(document):
#     s = open(document, 'r')
#     return web.Response(text=s.read(), content_type='text/html')


@routes.get('/')
async def index_handler(request):
    return web_response('test.txt')




@routes.get('/hello')
async def index_handler(request):
    return web.Response(text='Hello')


if __name__ == '__main__':
    print('server started')
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, host='127.0.0.1', port=2007)