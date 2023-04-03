import json

import aiohttp
import asyncio
import logging
from datetime import datetime
from utils import create_user, create_message, create_private_message



MENU = 'Welcome to chat. Commands:\n' \
         'Print "main" to enter main_chat\n' \
         'Push ctrl+c to quit\n' \
         'Print "add_message" to write message to main chat\n' \
         'Print username to write to private chat of the user\n' \
         '\n' \
         'ENTER YOUR COMMAND\n'





class Client():
    def __init__(self, url, username):
        self.url = url
        self.username = username

    async def show_status(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + 'info') as resp:
                print(await resp.text())


    # async def login(self, session, username: str) -> None:
    #     async with aiohttp.ClientSession() as session:
    #         async with session.post('http://localhost:2007/login', json={'name': username}) as resp:
    #             print(await resp.text())


    async def registration(self) -> None:
        async with aiohttp.ClientSession() as session:
            data = await create_user(self.username)
            async with session.post(self.url+'registration', data=json.dumps(data)) as resp:
                print(await resp.text())


    async def show_main_chat(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url+'main_chat') as resp:
                print(await resp.text())


    async def send_message_to_chat(self, message: str) -> None:
        async with aiohttp.ClientSession() as session:
            data = await create_message(self.username, message)
            async with session.post(self.url + 'main_chat', data=json.dumps(data)) as resp:
                print(await resp.text())


    async def send_message_to_user(self, receiver: str, message: str):
        """private chat"""
        async with aiohttp.ClientSession() as session:
            data = await create_private_message(self.username, receiver, message)
            async with session.post(self.url + 'private_chat' + self.username + '_' + receiver, data=json.dumps(data)) as resp:
                print(await resp.text())


    async def open_private_chat(self, receiver: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + 'private_chat/' + self.username + '_' + receiver) as resp:
                print(await resp.text())




async def main():
    client = Client('http://localhost:2007/', username='kolya',)
    # client = Client('http://localhost:2007/', username='julia',)

    # tasks = [client.registration()]
    # tasks = [
    #     client.handle_user('andrey'),
    #     client.send_message_to_chat(username='andrey', message='hello'),
    #     client.send_message_to_chat(username='masha', message='priuet'),
    # ]
    # tasks = [client.send_message_to_chat(message='salut'), client.show_main_chat()]
    # tasks = [client.show_main_chat()]

    tasks = [client.send_message_to_user('katya', 'test_1!')]# ,client.send_message_to_user('julia', 'test_2!')]

    # tasks = [client.open_private_chat('julia')]

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    #logging.info(MENU)

    asyncio.run(main())
