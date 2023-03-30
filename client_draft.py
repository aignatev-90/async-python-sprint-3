import aiohttp
import asyncio
import logging
from datetime import datetime



MENU = 'Welcome to chat. Commands:\n' \
         'Print "main" to enter main_chat\n' \
         'Push ctrl+c to quit\n' \
         'Print "add_message" to write message to main chat\n' \
         'Print username to write to private chat of the user\n' \
         '\n' \
         'ENTER YOUR COMMAND\n'

class Client():
    def __init__(self, url):
        self.url = url


    async def show status(self):
        #TODO
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:2007/') as resp:
                print(await resp.text())


    async def login(self, session, username: str) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.post('http://localhost:2007/login', json={'name': username}) as resp:
                print(await resp.text())


    async def registration(self, session, username: str) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url+'registration', data=username) as resp:
                print(await resp.text())


    async def handle_user(self, username: str) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url+'registration', data=username) as resp:
                print(await resp.text())
            async with session.post(self.url+'login', json={'name': username}) as resp:
                print(await resp.text())


    async def send_message_to_chat(self, username: str, message: str) -> None:
        async with aiohttp.ClientSession() as session:
            time = datetime.now().strftime('%d-%m-%Y %H:%M')
            text = time + ' ' + username + ': ' + message +'\n'   #### надо собрать словарь и разбирать его на стороне сервера, чтобы получить имя отправителя и проверить его на существование такого пользователя
            async with session.post(self.url + 'main_chat', data=text) as resp:
                print(await resp.text())


    async def send_message_to_user(self, username:str, receiver: str, message: str):
        #TODO
        pass


async def main():
    client = Client('http://localhost:2007/')
    tasks = [
        client.handle_user('andrey'),
        client.send_message_to_chat(username='andrey', message='hello'),
        client.send_message_to_chat(username='masha', message='priuet'),
    ]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    #logging.info(MENU)

    asyncio.run(main())
