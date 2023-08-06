import asyncio
import functools
import inspect
import json
from typing import Awaitable, Callable, Any

import pydantic


class App:
    def __init__(self):
        self._handlers: dict[str, Callable[[Any, ...], Awaitable[Any, Any, str | None]]] = {}
        self.users = {}

    # Private API
    async def _client_connected_callback(self, reader: asyncio.StreamReader,
                                         writer: asyncio.StreamWriter):
        address = writer.get_extra_info('peername')[1]
        writer.write(b'Welcome to the club, buddy ' + str(address).encode() + b'!\n')
        self.users[str(address)] = writer
        print(f'User {address} has connected')

        while True:
            data = await reader.readuntil()
            if not data.strip():
                break
            handler_name, *args = data.strip().decode().split()
            response = await self._get_response(handler_name, args)
            writer.write(response.encode())
            await writer.drain()

        print(f'User {address} has disconnected')
        writer.write(b'Goodbye!\n')
        self.users.pop(str(address))
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def _get_response(self, handler_name: str, args: list[str]) -> str:
        handler = self._handlers.get(handler_name)
        if not handler:
            return 'Unknown command\n'
        try:
            response = await handler(*args)
        except (TypeError, pydantic.ValidationError) as e:
            return str(e) + '\n'
        if response is None:
            return '\n'
        if not response.endswith('\n'):
            response += '\n'
        return response

    # Public API
    async def run(self, host='127.0.0.1', port=8888):
        server = await asyncio.start_server(self._client_connected_callback, host, port)
        addresses = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        print(f'Serving on {addresses}')
        async with server:
            await server.serve_forever()

    def command(self, name: str = None) -> callable:
        def inner(handler: callable) -> callable:
            @functools.wraps(handler)
            async def modified_handler(*arguments):
                modified_arguments = []
                handler_arguments_names = inspect.getfullargspec(handler)[0]
                if len(arguments) < len(handler_arguments_names):
                    raise TypeError('Missing some arguments')
                elif len(arguments) > len(handler_arguments_names):
                    raise TypeError('Some extra arguments were provided')
                for index, argument in enumerate(handler_arguments_names):
                    expected_type = handler.__annotations__.get(argument)
                    if expected_type is None:
                        raise TypeError('Please, provide annotations for all args')
                    if issubclass(expected_type, pydantic.BaseModel):
                        try:
                            argument_as_dict = json.loads(arguments[index])
                        except json.JSONDecodeError:
                            raise TypeError('Arguments for fields with pydantic types '
                                            'should represent JSON object '
                                            'without any whitespaces')
                        modified_argument = expected_type(**argument_as_dict)
                    else:
                        try:
                            modified_argument = expected_type(arguments[index])
                        except Exception:
                            raise TypeError(f'Failed to convert "{arguments[index]}" '
                                            f'to type {expected_type}')
                    modified_arguments.append(modified_argument)
                return await handler(*modified_arguments)

            if name:
                self._handlers[name] = modified_handler
            else:
                self._handlers[handler.__name__] = modified_handler
            return modified_handler

        return inner
