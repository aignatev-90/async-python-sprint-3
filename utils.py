from datetime import datetime
import asyncio
import os

from server_draft import Server


CWD = os.getcwd()
FOLDER = 'private_chats'


async def create_user(username: str) -> dict:
    data = {
                'id': 0,
                'name': username,
                'status': 'active',
                'ban_time': '',
                'messages_per_hour': 0,
            }
    return data


async def create_message(username: str, message: str) -> dict:
    data = {
                'id': 0,
                'author': username,
                'text': message,
                'time': str(datetime.now().strftime('%d-%m-%Y %H:%M')),
            }
    return data


# def create_private_chat(user_1: str, user_2: str):
#     if _user_exists(user_1, USERS) and _user_exists(user_2, USERS):
#         users = []
#         users.extend([user_1, user_2])
#         users.sort()
#         filename = str(users[0]) + str(users[1]) +'.json'
#         path = os.path.join(CWD, FOLDER, filename)
#         print(path)
#         with open(path, 'a') as f:
#             f.write('test')
#     else:
#         logging.error("Can't create chat. One of the users doesn't exist.")


async def create_private_message(author: str, receiver: str, message: str) -> dict:
    data = {
                'id': 0,
                'author': author,
                'receiver': receiver,
                'text': message,
                'time': str(datetime.now().strftime('%d-%m-%Y %H:%M')),
            }
    return data


def post_to_private_chat(sender, receiver, cwd, folder, req_data):
    users = []
    users.extend([sender, receiver])
    users.sort()
    filename = str(users[0]) + '_' + str(users[1]) + '.json'
    path = os.path.join(CWD, FOLDER, filename)
    message_id = Server._set_id(path, 'messages')
    data['id'] = message_id
    if os.path.exists(path):
        with open(path, 'r') as f:
            chat_entries = json.load(f)
            chat_entries['messages'].append(data)
        with open(path, 'w') as f:
            f.write(json.dumps(chat_entries, indent=4))
    else:
        holder = {"messages": [data]}
        with open(path, 'a') as f:
            f.write(json.dumps(holder, indent=4))

