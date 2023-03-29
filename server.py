import asyncio
import logging
import concurrent.futures


class EchoServer(object):
    """Echo server class"""

    def __init__(self, host, port, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._server = asyncio.start_server(self.handle_connection, host=host, port=port)

    def start(self, and_loop=True):
        self._server = self._loop.run_until_complete(self._server)
        logging.info('Listening established on {0}'.format(self._server.sockets[0].getsockname()))
        if and_loop:
            self._loop.run_forever()

    def stop(self, and_loop=True):
        self._server.close()
        if and_loop:
            self._loop.close()


    async def handle_connection(self, reader, writer):
        peername = writer.get_extra_info('peername')
        logging.info('Accepted connection from {}'.format(peername))
        while not reader.at_eof():
            try:
                writer.write(b'enter your login')
                user_login = await asyncio.wait_for(reader.readline(), timeout=10)
                logging.info('User {} entered'.format(user_login.decode()))
                writer.write(b'choose chat:\nmain - main chat\nprivate_chat')
                chosen_chat = await asyncio.wait_for(reader.readline(), timeout=10)
                logging.info('User {} chose chat {}'.format(user_login.decode(), chosen_chat.decode()))
                data = await asyncio.wait_for(reader.readline(), timeout=10)
                print(data)
                writer.write(data)
            except concurrent.futures.TimeoutError:
                break
        writer.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    server = EchoServer('127.0.0.1', 2007)
    try:
        server.start()
    except KeyboardInterrupt:
        pass  # Press Ctrl+C to stop
    finally:
        server.stop()
