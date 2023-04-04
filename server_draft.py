# import asyncio
import socket
from aiohttp import web
import json
import logging
import os
from datetime import datetime, timedelta


CWD = os.getcwd()
HOST = 'localhost'
PORT = 2007
USERS = 'users.json'  # users db
MAIN_CHAT = 'main_chat.json'
FOLDER = 'private_chats'

logging.basicConfig(level=logging.DEBUG)


class Server():
    def __init__(self, host: str, port: int, routes=None):
        self.host = host
        self.port = port
        self.routes = routes
        self.app = web.Application()
        self.show_messages = 20  # limit of messages in main chat shown to user
        self.time_limit = 0.5  # limit of time to check number of sent messages in hours
                             # and prevent user from sending new messages
        self.msg_limit = 4  # number of messages available to be sent from user during time_limit

    def add_routing(self, routes):
        if self.routes == None:
            self.app.add_routes(routes)

    def start(self):
        web.run_app(self.app, host=self.host, port=self.port)

    @staticmethod
    def _set_id(source: str, key: str) -> int:
        try:
            with open(source, 'r') as f:
                data = json.load(f)
                if len(data[key]) > 0:
                    object_id = int(data[key][-1]['id']) + 1
                else:
                    object_id = 1
            return object_id
        except (PermissionError, FileNotFoundError, FileExistsError):
            object_id = 1
        return object_id

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
    async def _show_chat(source_chat: str, entries: int) -> str:
        try:
            chat = ''
            output = ''
            with open(source_chat, 'r') as f:
                data = json.load(f)
                for entry in data['messages'][-entries:]:
                    chat += "{} {}: {} \n".format(entry['time'], entry['author'], entry['text'])
            return chat
        except (PermissionError, FileNotFoundError, FileExistsError):
            logging.error("Can't reach chat database")


    @staticmethod
    def _post_to_private_chat(sender, receiver, cwd, folder, req_data):
        users = []
        users.extend([sender, receiver])
        users.sort()
        filename = str(users[0]) + '_' + str(users[1]) + '.json'
        path = os.path.join(cwd, folder, filename)
        message_id = Server._set_id(filename, 'messages')
        req_data['id'] = message_id
        if os.path.exists(filename):
            print('exists')
            with open(filename, 'r') as f:
                chat_entries = json.load(f)
                chat_entries['messages'].append(req_data)
            with open(filename, 'w') as f:
                f.write(json.dumps(chat_entries, indent=4))
        else:
            holder = {
                "messages": [
                    req_data,
                ]
            }
            with open(filename, 'w') as file:
                json.dump(holder, file, indent=4)
        return path



    @staticmethod
    def _delete_old_messages(source: str, lifetime: int = 1) -> None:
        try:
            with open(source, 'r') as f:
                data = json.load(f)
                for message in data['messages']:
                    if datetime.strptime(message['time'], '%d-%m-%Y %H:%M') < datetime.now() - timedelta(hours=lifetime):
                        data['messages'].remove(message)
                        logging.info('Old messages deleted')
            with open(source, 'w') as f:
                f.write(json.dumps(data))
        except (PermissionError, FileNotFoundError, FileExistsError):
            logging.error("Failed to delete old messages. Can't access chat database. Source: {}".format(source))


    @staticmethod
    def _check_messages_limit(username: str, time_limit: (float, int), msg_limit: int) -> bool:
        """Counting messages of user in main chat per time period
         and deprive sending messages if msg_limit is reached"""
        try:
            with open(MAIN_CHAT, 'r') as f:
                data = json.load(f)
        except (PermissionError, FileNotFoundError, FileExistsError):
            logging.error("Can't open chat database. Failed to check number of messages")
        else:
            counter = 0
            for message in data['messages']:
                if message['author'] == username and \
                        datetime.strptime(message['time'], '%d-%m-%Y %H:%M') \
                        > datetime.now() - timedelta(hours=time_limit):
                    counter += 1
            if counter > msg_limit:
                return False
            return True


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
        self._delete_old_messages(MAIN_CHAT)
        response_obj = await Server._show_chat(MAIN_CHAT, self.show_messages)
        return web.Response(text=response_obj)


    async def post_to_main_chat(self, request):
        data = await request.json()
        username = data['author']
        if self._check_messages_limit(username=username, msg_limit=self.msg_limit, time_limit=self.time_limit):
            print('message_ limit_isnt reached')
            self._delete_old_messages(MAIN_CHAT)
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
                    response_obj = 'Message added'
                else:
                    response_obj = "Message wasn't sent. User with this username doesn't exist"
                    logging.info(response_obj)
            except (PermissionError, FileNotFoundError, FileExistsError):
                response_obj = "Can't connect to main chat database"
                logging.error(response_obj)
        else:
            response_obj = 'Max number of messages for user {} during time limit is reached'.format(username)
            logging.info(response_obj)
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


    async def post_to_private_chat(self, request):
        sender, receiver = request.match_info['users'].split('_')
        data = await request.json()
        print(data)
        if self._user_exists(sender, USERS) and self._user_exists(receiver, USERS):
            path = self._post_to_private_chat(sender=sender, receiver=receiver, cwd=CWD, folder=FOLDER, req_data=data)
            response_obj = 'Message added'
            logging.info('Message from {} to {} sent in private chat'.format(sender, receiver))
            self._delete_old_messages(path)
        else:
            logging.error("Can't create chat. One of the users doesn't exist.")
            response_obj = "Can't create chat. One of the users doesn't exist."
        return web.Response(text=response_obj)


    async def get_private_chat(self, request):
        user_1, user_2 = request.match_info['users'].split('_')
        users = []
        users.extend([user_1, user_2])
        users.sort()
        filename = str(users[0]) + '_' + str(users[1] + '.json')
        # path_to_chat = os.path.join(CWD, FOLDER, filename)
        self._delete_old_messages(filename)
        response_obj = await Server._show_chat(filename, self.show_messages)
        return web.Response(text=response_obj)


if __name__ == '__main__':
    server = Server(host='localhost', port=2007)
    server.add_routing([
        web.post('/registration', server.registration),
        web.post('/main_chat', server.post_to_main_chat),
        web.get('/main_chat', server.get_main_chat),
        web.get('/info', server.show_status),
        web.post('/private_chat{users}', server.post_to_private_chat),
        web.get('/private_chat/{users}', server.get_private_chat),
    ])
    server.start()
