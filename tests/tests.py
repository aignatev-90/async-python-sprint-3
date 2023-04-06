import asyncio
import os
import unittest
from server import Server
import asyncio
from utils import create_private_message
from private_chat_post_check import test_data


class ServerUtilsTest(unittest.TestCase):

    def setUp(self) -> None:
        self.s = Server('localhost', 8000)
        self.set_id_test_file_1 = ('set_id_check_1.json', 'users')
        self.set_id_test_file_2 = ('set_id_check_2.json', 'messages')
        self.set_id_test_file_3 = ('doesnt_exist.json', 'anything')
        self.USERS = 'user_exists_check.json'
        self.MAIN_CHAT = 'show_main_chat_check.json'
        self.PRIVATE_CHAT = 'show_private_chat_check.json'
        self.req_data = test_data
        self.cwd = os.getcwd()

    def test_set_id(self) -> None:
        self.assertEqual(self.s._set_id(*self.set_id_test_file_1), 3)
        self.assertEqual(self.s._set_id(*self.set_id_test_file_2), 4)
        self.assertEqual(self.s._set_id(*self.set_id_test_file_3), 1)

    def test_user_exists(self) -> None:
        self.assertTrue(self.s._user_exists('katya', self.USERS))
        self.assertTrue(self.s._user_exists('petya', self.USERS))
        self.assertFalse(self.s._user_exists('julia', self.USERS))
        self.assertFalse(self.s._user_exists('nastya', self.USERS))

    async def test_show_chat(self) -> None:
        task1 = await self.s._show_chat(self.MAIN_CHAT, entries=20)
        task2 = await self.s._show_chat(self.PRIVATE_CHAT, entries=20)
        self.assertIsInstance(task1, str)
        self.assertIsInstance(task2, str)

    def test_post_to_private_chat(self) -> None:
        self.assertIsInstance(self.s._post_to_private_chat('katya', 'julia', self.cwd, self.req_data), str)
