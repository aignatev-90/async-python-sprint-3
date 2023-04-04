from datetime import datetime
import asyncio
import os

from server_draft import Server


CWD = os.getcwd()
FOLDER = 'private_chat'


async def create_user(username: str) -> dict:
    data = {
                'id': 0,
                'name': username,
                'status': 'active',
                'strikes': 0,
                'ban_time': '',
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
    return path
