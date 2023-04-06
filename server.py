import json
import logging
import os
from datetime import datetime, timedelta

from aiohttp import web

CWD = os.getcwd()
HOST = 'localhost'
PORT = 2007
USERS = 'dbs/users.json'  # users db
MAIN_CHAT = 'dbs/main_chat.json'

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
        self.msg_limit = 50  # number of messages available to be sent from user during time_limit
        self.strikes = 3  # number of strikes for user to be banned
        self.ban_time = 1  # period of time for user to be banned if got number of strikes == self.strikes

    def add_routing(self, routes: list) -> None:
        if not self.routes:
            self.app.add_routes(routes)

    def start(self) -> None:
        if not os.path.exists(CWD + '/dbs'):
            os.mkdir(CWD + '/dbs')

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
        except (PermissionError, FileNotFoundError):
            object_id = 1
        return object_id

    @staticmethod
    def _user_exists(user: str, users_db) -> bool:
        try:
            with open(users_db, 'r') as f:
                data = json.load(f)
            try:
                for u in data['users']:
                    if str(user) == u['name']:
                        return True
                return False
            except (KeyError, ValueError):
                logging.error("Can't get information about user. Wrong database format")
                return False
        except (PermissionError, FileNotFoundError):
            logging.error("Can't reach users database. Failed to log in")
            return False

    @staticmethod
    async def _show_chat(source_chat: str, entries: int) -> str:
        try:
            chat = ''
            with open('dbs/' + source_chat, 'r') as f:
                data = json.load(f)
                try:
                    if len(data['messages']) == 0:
                        return 'Chat is empty'
                    for entry in data['messages'][-entries:]:
                        chat += "{} {}: {} \n".format(entry['time'], entry['author'], entry['text'])
                except (KeyError, ValueError):
                    error = "Can't show main chat. Wrong database format"
                    logging.error(error)
                    return error
            return chat
        except (PermissionError, FileNotFoundError):
            logging.error(f"Can't reach chat database {source_chat}")

    @staticmethod
    def _post_to_private_chat(sender: str, receiver: str, cwd: str, req_data: dict) -> str:
        users = []
        users.extend([sender, receiver])
        users.sort()
        filename = 'dbs/' + str(users[0]) + '_' + str(users[1]) + '.json'
        path = os.path.join(cwd, filename)
        message_id = Server._set_id(filename, 'messages')
        try:
            req_data['id'] = message_id
        except (KeyError, ValueError):
            logging.error('Bad request. Wrong request format')
            return web.Response(text='Wrong request format', status=400)
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    chat_entries = json.load(f)
                    chat_entries['messages'].append(req_data)
                with open(filename, 'w') as f:
                    f.write(json.dumps(chat_entries, indent=4))
            except (PermissionError, FileNotFoundError):
                logging.error("Can't reach chat database")
        else:
            holder = {
                "messages": [
                    req_data,
                ]
            }
            try:
                with open(filename, 'w') as file:
                    json.dump(holder, file, indent=4)
            except (PermissionError, FileNotFoundError):
                logging.error("Can't create chat database")
        return path

    @staticmethod
    def _delete_old_messages(source: str, lifetime: int = 1) -> None:
        try:
            with open(source, 'r') as f:
                data = json.load(f)
                try:
                    for message in data['messages']:
                        if datetime.strptime(
                                message['time'], '%d-%m-%Y %H:%M'
                        ) < datetime.now() - timedelta(hours=lifetime):
                            data['messages'].remove(message)
                            logging.info('Old messages deleted')
                except (KeyError, ValueError):
                    logging.error(
                        f"Failed to delete old messages."
                        f" Can't access chat database. Source: {source}")
            with open(source, 'w') as f:
                f.write(json.dumps(data, indent=4))
        except (PermissionError, FileNotFoundError):
            logging.error(
                "Failed to delete old messages."
                " Can't access chat database. Source: {}".format(source))

    @staticmethod
    def _check_messages_limit(username: str, time_limit: (float, int), msg_limit: int) -> bool:
        """Counting messages of user in main chat per time period
         and deprive sending messages if msg_limit is reached"""
        try:
            with open(MAIN_CHAT, 'r') as f:
                data = json.load(f)
        except (PermissionError, FileNotFoundError):
            logging.error("Can't open chat database. Failed to check number of messages")
            return True
        else:
            counter = 0
            try:
                for message in data['messages']:
                    if message['author'] == username and \
                            datetime.strptime(message['time'], '%d-%m-%Y %H:%M') \
                            > datetime.now() - timedelta(hours=time_limit):
                        counter += 1
            except (KeyError, ValueError):
                logging.error("Can't check number of messages. Wrong file format")
                return True
            else:
                if counter > msg_limit:
                    return False
                return True

    @staticmethod
    def _is_banned(username: str) -> bool:
        try:
            with open(USERS, 'r') as f:
                data = json.load(f)
        except (PermissionError, FileNotFoundError):
            logging.error("Failed to reach users database. Can't check if user is banned")
            return False
        else:
            try:
                for user in data['users']:
                    if user['name'] == username and \
                            datetime.strptime(user['ban_time'], '%Y-%m-%d %H:%M:%S.%f') > datetime.now():
                        return True
                    return False
            except (ValueError, KeyError):
                return False

    def _ban_users(self) -> None:
        try:
            with open(USERS, 'r') as f:
                data = json.load(f)
        except (PermissionError, FileNotFoundError):
            logging.error("Failed to reach users database. Can't ban user")
        else:
            try:
                for user in data['users']:
                    number_of_strikes = user['strikes']
                    if number_of_strikes != 0 and number_of_strikes % self.strikes == 0:
                        user['ban_time'] = str(datetime.now() + timedelta(hours=self.ban_time))
            except (KeyError, ValueError):
                logging.error("Something wrong with users file. Can't ban users")
            try:
                with open(USERS, 'w') as f:
                    json.dump(data, f, indent=4)
                logging.info('Users list was checked for bans')
            except (PermissionError, FileNotFoundError):
                logging.error("Failed to reach users database. Can't ban user")

    async def registration(self, request):
        data = await request.json()
        try:
            username = data['name']
        except (KeyError, ValueError):
            logging.error('Bad request. Wrong request format')
            return web.Response(text='Wrong request format', status=400)
        if not os.path.exists(USERS):
            data['id'] = self._set_id(USERS, 'users')
            d = {"users": [data]}
            try:
                with open(USERS, 'w') as f:
                    json.dump(d, f, indent=4)
            except (PermissionError, FileNotFoundError) as e:
                response_obj = str(e) + '\n'
            else:
                response_obj = f'user {username} successfully created' + '\n'
        else:
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
                    response_obj = f'user {username} successfully created' + '\n'
                else:
                    response_obj = f'user {username} already exists' '\n'
            except (PermissionError, FileNotFoundError) as e:
                logging.info('Failed creating user {}. {}'.format(username, str(e)))
                response_obj = {'status': 'failed', 'message': str(e)}

        return web.Response(text=response_obj, status=200)

    async def get_main_chat(self, request):
        self._delete_old_messages(MAIN_CHAT)
        response_obj = await self._show_chat(MAIN_CHAT, self.show_messages)
        return web.Response(text='\n' + response_obj + '\n', status=200)

    async def post_to_main_chat(self, request):
        data = await request.json()
        try:
            username = data['author']
        except (KeyError, ValueError):
            logging.error('Bad request. Wrong request format')
            return web.Response(text='Wrong request format', status=400)

        if self._check_messages_limit(username=username, msg_limit=self.msg_limit, time_limit=self.time_limit) \
                and not self._is_banned(username):
            if not os.path.exists(MAIN_CHAT):
                data['id'] = self._set_id(MAIN_CHAT, 'messages')
                d = {"messages": [data]}
                try:
                    with open(MAIN_CHAT, 'w') as f:
                        json.dump(d, f, indent=4)
                    response_obj = 'Message from {} successfully added'.format(username)
                except (PermissionError, FileNotFoundError):
                    response_obj = "Can't post message to main chat. Can't access database"
                    logging.error(response_obj)
                return web.Response(text='\n' + response_obj + '\n', status=200)
            else:
                try:
                    self._delete_old_messages(MAIN_CHAT)
                    if self._user_exists(str(username), USERS):
                        message_id = Server._set_id(MAIN_CHAT, 'messages')
                        with open(MAIN_CHAT, 'r') as f:
                            try:
                                data['id'] = message_id
                            except (KeyError, ValueError):
                                response_obj = "Wrong file format for main chat database. Can't add message"
                                logging.error(response_obj)
                            else:
                                chat_entries = json.load(f)
                                try:
                                    chat_entries['messages'].append(data)
                                except (KeyError, ValueError):
                                    response_obj = "Wrong file format for main chat database. Can't add message"
                                    logging.error(response_obj)
                        with open(MAIN_CHAT, 'w') as f:
                            f.write(json.dumps(chat_entries, indent=4))
                        response_obj = 'Message from user %s added' % username
                        logging.info(response_obj)
                    else:
                        response_obj = "Message wasn't sent. User with this username doesn't exist"
                        logging.info(response_obj)
                    return web.Response(text='\n' + response_obj + '\n', status=200)
                except (PermissionError, FileNotFoundError):
                    response_obj = "Can't connect to main chat database"
                    logging.error(response_obj)
        else:
            response_obj = 'Max number of messages for user {}' \
                           ' during time limit is reached or user is banned'.format(username)
            logging.info(response_obj)
            return web.Response(text='\n' + response_obj + '\n', status=200)

    async def show_status(self, request):
        response_obj = 'Current users:\n'
        try:
            with open(USERS, 'r') as f:
                data = f.read()
            users_data = json.loads(data)
            try:
                for user in users_data['users']:
                    response_obj += user['name'] + '\n'
            except (KeyError, ValueError):
                response_obj = "Wrong file format for users database. Can't show users"
                logging.error(response_obj)
        except (PermissionError, FileNotFoundError):
            response_obj = 'Database error. No information found'
        return web.Response(text='\n' + response_obj + '\n', status=200)

    async def post_to_private_chat(self, request):
        try:
            sender, receiver = request.match_info['users'].split('_')
        except (KeyError, ValueError):
            logging.error('Bad request. Wrong request format')
            return web.Response(text='Wrong request format', status=400)
        else:
            data = await request.json()
            if self._user_exists(sender, USERS) and self._user_exists(receiver, USERS):
                path = self._post_to_private_chat(sender=sender, receiver=receiver, cwd=CWD, req_data=data)
                response_obj = 'Message added'
                logging.info('Message from {} to {} sent in private chat'.format(sender, receiver))
                self._delete_old_messages(path)
            else:
                logging.error("Can't create chat. One of the users doesn't exist.")
                response_obj = "Can't create chat. One of the users doesn't exist."
            return web.Response(text='\n' + response_obj + '\n', status=200)

    async def get_private_chat(self, request):
        try:
            user_1, user_2 = request.match_info['users'].split('_')
        except (KeyError, ValueError):
            logging.error('Bad request. Wrong request format')
            return web.Response(text='Wrong request format', status=400)
        else:
            users = []
            users.extend([user_1, user_2])
            users.sort()
            filename = str(users[0]) + '_' + str(users[1] + '.json')
            self._delete_old_messages(filename)
            response_obj = await self._show_chat(filename, self.show_messages)
            return web.Response(text='\n' + response_obj + '\n', status=200)

    async def add_strike(self, request):
        try:
            username = request.match_info['name']
        except (KeyError, ValueError):
            logging.error('Bad request. Wrong request format')
            return web.Response(text='Wrong request format', status=400)
        else:
            if self._user_exists(username, USERS):
                try:
                    with open(USERS, 'r') as f:
                        data = json.load(f)
                except (PermissionError, FileNotFoundError, FileExistsError):
                    response_obj = "Failed to reach users db. Can't add strike"
                    logging.info(response_obj)
                else:
                    for user in data['users']:
                        if user['name'] == username:
                            strikes = int(user['strikes'])
                            strikes += 1
                            user['strikes'] = strikes
                    with open(USERS, 'w') as f:
                        json.dump(data, f, indent=4)
                    self._ban_users()
                    response_obj = 'Strike for user {} added'.format(username)
            else:
                response_obj = "User doesn't exist"
            return web.Response(text='\n' + response_obj + '\n', status=200)


if __name__ == '__main__':
    server = Server(host='localhost', port=2007)
    server.add_routing([
        web.post('/registration', server.registration),
        web.post('/main_chat', server.post_to_main_chat),
        web.get('/main_chat', server.get_main_chat),
        web.get('/info', server.show_status),
        web.post('/private_chat{users}', server.post_to_private_chat),
        web.get('/private_chat/{users}', server.get_private_chat),
        web.post('/strike/{name}', server.add_strike)
    ])
    server.start()
