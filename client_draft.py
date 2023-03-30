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
        async with session.get('http://localhost:2007/') as resp:
            print(await resp.text())


async def login(username: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:2007/login', json={'name': username}) as resp:
            print(await resp.text())


async def registration(username: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:2007/registration', data=username) as resp:
            print(await resp.text())


async def main():
    tasks = [registration('masha'), registration('pasha'), registration('dasha')]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    #logging.info(MENU)

    asyncio.run(main())
