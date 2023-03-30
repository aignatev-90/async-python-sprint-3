# import asyncio
import socket
from aiohttp import web
import json
import logging

HOST = 'localhost'
PORT = 2007
USERS = 'users.json' #users db
MAIN_CHAT = 'main_chat.txt'

logging.basicConfig(level=logging.DEBUG)

class Server():
    def __init__(self, host: str, port: int, routes=None):
        self.host = host
        self.port = port
        self.routes = routes
        self.app = web.Application()

    def add_routing(self, routes):
        if self.routes == None:
            self.app.add_routes(routes)

    def start(self):
        web.run_app(self.app, host=self.host, port=self.port)

    @staticmethod
    def _user_exists(user, users_db):
        try:
            with open(users_db) as f:
                for line in f:
                    if str(user) in line:
                        return True
                return False
        except PermissionError:
            logging.error("Can't reach users database. Failed to log in")
            return False


    @staticmethod
    def _show_main_chat(entries: int) -> str:
        try:
            chat = ''
            with open(MAIN_CHAT, 'r') as f:
                lines = f.readlines()
                total_length = len(lines)
                print(total_length)
                threshold = total_length - entries

                for line_num, line in enumerate(lines):
                    if line_num >= threshold:
                        chat += ''.join(line)
                return chat
        except PermissionError:
            logging.error("Can't reach main chat database")



    async def login(self, request):
        try:
            data = await request.json() # dict
            username = data['name']
            if Server._user_exists(str(username), USERS):
                logging.info('User {} logged in'.format(username))
                response_obj = Server._show_main_chat(4)
                return web.Response(text=response_obj, status=200)
            else:
                logging.info('User {} not found'.format(username))
                response_obj = { 'status': 'failed', 'message': f'user {username} not found' }
            return web.Response(text=json.dumps(response_obj), status=200)
        except Exception as e:
            response_obj = { 'status': 'failed', 'message': str(e) }
            return web.Response(text=json.dumps(response_obj), status=500)


    async def registration(self, request):
        data = await request.text()  # dict
        username = str(data)
        try:
            logging.info('Creating user {}'.format(username))
            with open(USERS, 'a') as f:
                if not Server._user_exists(str(username), USERS):
                    f.write(json.dumps(username)+ '\n')
                    response_obj = {'status': 'success', 'message': f'user {username} successfully created'}
                else:
                    response_obj = {'status': 'failure', 'message': f'user {username} already exists'}
            return web.Response(text=json.dumps(response_obj), status=200)
        except PermissionError as e:
            logging.info('Failed creating user {}. {}'.format(username, str(e)))
            response_obj = { 'status': 'failed', 'message': str(e) }
            return web.Response(text=json.dumps(response_obj), status=500)
        except Exception as e:
            logging.info('Failed creating user {}. {}'.format(username, str(e)))
            response_obj = { 'status': 'failed', 'message': str(e) }
            return web.Response(text=json.dumps(response_obj), status=500)

    async def post_to_main_chat(self, request):
        # data = await request
        pass



if __name__ == '__main__':
    server = Server(host='localhost', port=2007)
    server.add_routing([
        web.post('/registration', server.registration),
        web.post('/login', server.login),
        web.post('/main_chat', server.post_to_main_chat)
    ])
    server.start()
