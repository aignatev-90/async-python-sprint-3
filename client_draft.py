import aiohttp
import asyncio
import logging

MENU = 'Welcome to chat. Commands:\n' \
         'Print "main" to enter main_chat\n' \
         'Push ctrl+c to quit\n' \
         'Print "add_message" to write message to main chat\n' \
         'Print username to write to private chat of the user\n' \
         '\n' \
         'ENTER YOUR COMMAND\n'


async def show_main_chat(session):
    async with session.get('http://localhost:2007/main') as resp:
        print(await resp.text())


async def create_session():
    session = aiohttp.ClientSession()
    return session


async def main_chat():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:2007/main') as resp:
            # print(resp.status)
            print(await resp.text())


async def hello_chat():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:2007/hello') as resp:
            # print(resp.status)
            print(await resp.text())


async def main():
    async with aiohttp.ClientSession('http://127.0.0.1:2007') as session:
        async with session.get('/get') as resp:
            print(await resp.text())
        async with session.post('/post', data=)
            print(await resp.text())





while True:
    logging.basicConfig(level=logging.DEBUG)
    logging.info(MENU)
    # session = asyncio.run(create_session())
    command = input()
    if command == 'main':
        asyncio.run(hello_chat())
    # if command == 'hello':
    #     asyncio.run(hello_chat())


