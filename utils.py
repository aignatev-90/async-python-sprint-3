from datetime import datetime
import asyncio


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

