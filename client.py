import asyncio
import json
import logging
import sys

import aiohttp

from utils import MENU, create_message, create_private_message, create_user


class Client():
    def __init__(self, url, username):
        self.url = url
        self.username = username

    async def show_status(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + 'info') as resp:
                print(await resp.text())

    async def registration(self) -> None:
        async with aiohttp.ClientSession() as session:
            data = await create_user(self.username)
            async with session.post(self.url + 'registration', data=json.dumps(data)) as resp:
                print(await resp.text())

    async def show_main_chat(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + 'main_chat') as resp:
                print(await resp.text())

    async def send_message_to_chat(self, message: str) -> None:
        async with aiohttp.ClientSession() as session:
            data = await create_message(self.username, message)
            async with session.post(self.url + 'main_chat', data=json.dumps(data)) as resp:
                print(await resp.text())

    async def send_message_to_user(self, receiver: str, message: str) -> None:
        """private chat"""
        async with aiohttp.ClientSession() as session:
            data = await create_private_message(self.username, receiver, message)
            async with session.post(
                    self.url + 'private_chat' + self.username + '_' + receiver, data=json.dumps(data)
            ) as resp:
                print(await resp.text())

    async def open_private_chat(self, receiver: str) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    self.url + 'private_chat/' + self.username + '_' + receiver
            ) as resp:
                print(await resp.text())

    async def send_strike(self, receiver: str) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url + 'strike/' + receiver, data=receiver) as resp:
                print(await resp.text())


if __name__ == '__main__':
    tasks = []
    logging.basicConfig(level=logging.DEBUG)

    async def main():
        logging.info('Enter username:\n')
        username = str(input())
        client = Client('http://localhost:2007/', username=username,)

        while True:
            logging.info(MENU)
            command = str(input())
            try:
                if 'show_main_chat' in command:
                    t = asyncio.create_task(client.show_main_chat())
                elif 'show_users' in command:
                    t = asyncio.create_task(client.show_status())
                elif 'registration' in command:
                    t = asyncio.create_task(client.registration())
                elif 'send_message_to_chat' in command:
                    com, text = command.split(' ')
                    t = asyncio.create_task(client.send_message_to_chat(text))
                elif 'show_private_chat' in command:
                    com, user = command.split(' ')
                    t = asyncio.create_task(client.open_private_chat(user))
                elif 'write_to_user' in command:
                    com, user, msg = command.split(' ')
                    t = asyncio.create_task(client.send_message_to_user(user, msg))
                elif 'send_strike' in command:
                    com, user = command.split(' ')
                    t = asyncio.create_task(client.send_strike(user))
                else:
                    logging.info('Wrong command. Try again\n')
            except ValueError:
                logging.info('Wrong command. Try again\n')

            await t

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('C ya!')
        sys.exit(130)
