# import asyncio
import socket
from aiohttp import web
import json
import logging
import os

HOST = 'localhost'
PORT = 2007
USERS = 'users.json'  # users db
MAIN_CHAT = 'main_chat.json'
# USERS_IDs = 'user_id.txt'

logging.basicConfig(level=logging.DEBUG)

class Server():
    def __init__(self, host: str, port: int, limiter, routes=None):
        self.host = host
        self.port = port
        self.routes = routes
        self.app = web.Application()
        self.limiter = limiter  # limit of messages in main chat shown to user


    def add_routing(self, routes):
        if self.routes == None:
            self.app.add_routes(routes)


    def start(self):
        web.run_app(self.app, host=self.host, port=self.port)


    @staticmethod
    def _set_id(source: str, type: str) -> int:
        try:
            with open(source, 'r') as f:
                data = json.load(f)
                print(data)
                if len(data[type]) > 0:
                    print(len(data))
                    object_id = int(data[type][-1]['id']) + 1
                else:
                    object_id = 1
            return object_id
        except (PermissionError, FileNotFoundError, FileExistsError):
            logging.error("Can't reach users database. Failed to log in")


    @staticmethod
    def _user_exists(user: str, users_db) -> bool:
        try:
            with open(users_db, 'r') as f:
                data = json.load(f)
            for u in data['users']:
                if str(user) == u['name']:
                    return True
            return False
        except (PermissionError, FileNotFoundError, FileExistsError):
            logging.error("Can't reach users database. Failed to log in")
            return False


    @staticmethod
    async def _show_main_chat(entries: int) -> str:
        try:
            chat = ''
            output = ''
            with open(MAIN_CHAT, 'r') as f:
                data = json.load(f)
                for entry in data['messages'][-entries:]:
                    chat += "{} {}: {} \n".format(entry['time'], entry['author'], entry['text'])
            print(chat)
            return chat
        except (PermissionError, FileNotFoundError, FileExistsError):
            logging.error("Can't reach main chat database")



    # async def login(self, request):
    #     try:
    #         data = await request.json() # dict
    #         username = data['name']
    #         if Server._user_exists(str(username), USERS):
    #             logging.info('User {} logged in'.format(username))
    #             response_obj = 'Successfully logged in\n' + Server._show_main_chat(4)
    #             return web.Response(text=response_obj, status=200)
    #         else:
    #             logging.info('User {} not found'.format(username))
    #             response_obj = { 'status': 'failed', 'message': f'user {username} not found' }
    #         return web.Response(text=json.dumps(response_obj), status=200)
    #     except Exception as e:
    #         response_obj = { 'status': 'failed', 'message': str(e) }
    #         return web.Response(text=json.dumps(response_obj), status=500)


    async def registration(self, request):
        data = await request.json()
        username = data['name']
        print(data)
        try:
            logging.info('Trying to create user {}'.format(username))
            with open(USERS, 'r') as f:
                users_entries = json.load(f)
            if not self._user_exists(str(username), USERS):
                user_id = Server._set_id(USERS, 'users')
                data['id'] = user_id
                users_entries['users'].append(data)
                with open(USERS, 'w') as f:
                    f.write(json.dumps(users_entries, indent=4))
                response_obj = {'status': 'success', 'message': f'user {username} successfully created'}
            else:
                response_obj = {'status': 'failure', 'message': f'user {username} already exists'}
            return web.Response(text=json.dumps(response_obj), status=200)
        except (PermissionError, FileNotFoundError, FileExistsError):
            logging.info('Failed creating user {}. {}'.format(username, str(e)))
            response_obj = { 'status': 'failed', 'message': str(e) }
            return web.Response(text=json.dumps(response_obj), status=500)


    async def get_main_chat(self, request):
        response_obj = await Server._show_main_chat(self.limiter)
        return web.Response(text=response_obj)


    async def post_to_main_chat(self, request):
        data = await request.json()
        username = data['author']
        try:
            if self._user_exists(str(username), USERS):
                message_id = Server._set_id(MAIN_CHAT, 'messages')
                with open(MAIN_CHAT, 'r') as f:
                    data['id'] = message_id
                    chat_entries = json.load(f)
                    chat_entries['messages'].append(data)
                with open(MAIN_CHAT, 'w') as f:
                    f.write(json.dumps(chat_entries, indent=4))
                logging.info('Message added')
                # response_obj = await Server._show_main_chat(self.limiter)
                response_obj = 'Message added'
            else:
                response_obj = "Message wasn't sent. User with this username doesn't exist"
                logging.info(response_obj)
                return web.Response(text=response_obj)
        except (PermissionError, FileNotFoundError, FileExistsError):
            response_obj = "Can't connect to main chat database"
            logging.error(response_obj)
        return web.Response(text=response_obj)


    async def show_status(self, request):
        response_obj = 'Current users:\n'
        try:
            with open(USERS, 'r') as f:
                data = f.read()
            users_data = json.loads(data)
            for user in users_data['users']:
                response_obj += user['name'] + '\n'
        except (PermissionError, FileNotFoundError, FileExistsError):
            response_obj = 'Database error. No information found'
        return web.Response(text=response_obj)



if __name__ == '__main__':
    server = Server(host='localhost', port=2007, limiter=4)
    server.add_routing([
        web.post('/registration', server.registration),
        # web.post('/login', server.login),
        web.post('/main_chat', server.post_to_main_chat),
        web.get('/main_chat', server.get_main_chat),
        web.get('/info', server.show_status),
    ])
    server.start()
