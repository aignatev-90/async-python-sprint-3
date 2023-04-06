from datetime import datetime

MENU = 'Welcome to chat. Commands:\n' \
       'Print "show_users" to see list of users\n' \
       'Print "show_main_chat" to enter main_chat\n' \
       'Print "registration" to register\n' \
       'Print "send_message_to_chat <your message>" to write to main chat\n' \
       'Print "show_private_chat <username>" to write to users private chat\n' \
       'Print "write_to_user <username> <your message>" to write to users private chat\n' \
       'Print "send_strike <username>" to send strike for user\n' \
       'Push ctrl+c to quit\n' \
       '\n' \
       'ENTER YOUR COMMAND\n'


async def create_user(username: str) -> dict:
    data = {
                'id': 0,
                'name': username,
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
