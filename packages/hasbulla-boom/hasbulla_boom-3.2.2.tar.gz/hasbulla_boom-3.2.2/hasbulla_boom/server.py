import functools
import random
from asyncio import StreamReader, StreamWriter

import asyncio

from hasbulla_boom.database import db
from hasbulla_boom.encryption import Encryptor


class Server:
    def __init__(self, host: str = "localhost", port: int = 8888):
        self.host = host
        self.port = port
        self.users = []

    @staticmethod
    def register_command(*types):
        len_types = len(types)

        def decorator(func):
            @functools.wraps(func)
            def wrapper(user_id: int, *args, **kwargs):
                assert len_types == len(args) + len(kwargs) + 1, f'Get command takes exactly {len_types - 1} arguments'
                for i in range(1, len_types):
                    assert types[i].validate(args[i - 1])
                return func(user_id, *args, **kwargs)
            db.commands_dict[func.__name__] = wrapper
            return wrapper
        return decorator

    @staticmethod
    def handle_command(user_id: int, cmd: str, *args) -> str:
        try:
            command_func = db.commands_dict.get(cmd)
            if command_func is None:
                raise ValueError('Unknown command')
            result = command_func(user_id, *args)
        except (TypeError, ValueError, AssertionError) as e:
            result = str(e)
        except StopIteration:
            result = ''
        return result

    @staticmethod
    async def keys_exchange(reader: StreamReader, writer: StreamWriter) -> Encryptor:
        public_key = random.randint(1000, 10000)
        private_key = random.randint(1000, 10000)
        writer.write((str(public_key) + "\n").encode('utf8'))
        await writer.drain()
        client_public_key = int((await reader.readline()).decode('utf8'))
        encryptor = Encryptor(public_key, client_public_key, private_key)
        writer.write((str(encryptor.generate_partial_key()) + "\n").encode('utf8'))
        await writer.drain()
        client_partial_key = int((await reader.readline()).decode('utf8'))
        encryptor.generate_full_key(client_partial_key)
        return encryptor

    @staticmethod
    async def get_notifications(user_id: int, writer: StreamWriter, encryptor: Encryptor) -> None:
        if db.notifications[user_id]:
            response = "\n".join([i for i in db.notifications[user_id]])
            db.notifications[user_id] = []
            writer.write((encryptor.encrypt_message(response) + "\n").encode('utf8'))
            await writer.drain()

    async def handle_client(self, reader: StreamReader, writer: StreamWriter) -> None:
        user_id = len(self.users)
        self.users.append(user_id)
        db.notifications[user_id] = []
        encryptor = await self.keys_exchange(reader, writer)
        writer.write((encryptor.encrypt_message("Hi client") + "\n").encode('utf8'))
        await writer.drain()
        request = encryptor.decrypt_message((await reader.readline()).decode('utf8').rstrip('\n'))
        while request:
            result = self.handle_command(user_id, *request.split())
            if result == "stop":
                break
            await self.get_notifications(user_id, writer, encryptor)
            response = encryptor.encrypt_message(result) + '\n'
            writer.write(response.encode('utf8'))
            await writer.drain()
            await self.get_notifications(user_id, writer, encryptor)
            request = encryptor.decrypt_message((await reader.readline()).decode('utf8').rstrip('\n'))

        writer.close()

    async def run(self) -> None:
        server = await asyncio.start_server(self.handle_client, self.host, self.port)

        async with server:
            await server.serve_forever()
