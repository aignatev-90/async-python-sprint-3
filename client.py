import asyncio
import json
import logging
import sys

import aiohttp

from commands import Commands
from settings import Settings
from utils import MENU, create_message, create_private_message, create_user


class Client:
    def __init__(self, url: str, username: str):
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
    settings = Settings()

    async def main():
        logging.info('Enter username:\n')
        username = str(input())
        url = settings.APP_PROTO + '://' + settings.APP_HOST + ':' + str(settings.APP_PORT) + '/'
        client = Client(url, username=username,)

        while True:
            logging.info(MENU)
            command = str(input()).split(' ')
            try:
                match command[0]:
                    case Commands.show_main_chat.name:
                        t = asyncio.create_task(client.show_main_chat())
                    case Commands.show_users.name:
                        t = asyncio.create_task(client.show_status())
                    case Commands.registration.name:
                        t = asyncio.create_task(client.registration())
                    case Commands.send_message_to_chat.name:
                        text = command[1]
                        t = asyncio.create_task(client.send_message_to_chat(text))
                    case Commands.show_private_chat.name:
                        user = command[1]
                        t = asyncio.create_task(client.open_private_chat(user))
                    case Commands.write_to_user.name:
                        user = command[1]
                        msg = command[2]
                        t = asyncio.create_task(client.send_message_to_user(user, msg))
                    case Commands.send_strike.name:
                        user = command[1]
                        t = asyncio.create_task(client.send_strike(user))
                    case _:
                        logging.info('Wrong command. Try again\n')
                        t = asyncio.sleep(0.01)
            except (ValueError, IndexError):
                logging.info('Wrong command. Try again\n')
                t = asyncio.sleep(0.01)

            await t

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('C ya!')
        sys.exit(130)
