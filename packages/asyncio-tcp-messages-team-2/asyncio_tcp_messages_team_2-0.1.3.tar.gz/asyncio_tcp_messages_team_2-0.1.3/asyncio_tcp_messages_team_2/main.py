import asyncio
import re


class MySocketLib:
    def __init__(self, address: str, port: int):
        self.address = address
        self.port = port
        self.commands_dict = dict()
        self.clients = {}

    def command(self, func: callable) -> callable:
        self.commands_dict[func.__name__] = func

        async def inner(*args, **kwargs) -> callable:
            return await func(*args, **kwargs)

        return inner

    async def check_args(self, command: str, args: dict, dict_args) -> bool:
        for arg in args:
            try:
                if type(args[arg]) != dict_args[arg]:
                    try:
                        args[arg] = int(args[arg])
                        continue
                    except ValueError:
                        return False
            except KeyError:
                return False
        return True

    async def correct_command_and_args(self, message: str) -> tuple:
        args = {}
        # first component of command second keys third values
        components = re.split(" --key | --val |\\n", message)

        # delete void
        clear_components = []
        for component in components:
            if component:
                clear_components.append(component)

        command = clear_components[0]
        if len(clear_components) == 3:
            keys, vals = clear_components[1].split(), clear_components[2].split()
            if len(keys) != len(vals):
                return "Error: ", f"The number of keys differs from the arguments keys: {len(keys)}, vals: {len(vals)}"
            for key, val in zip(keys, vals):
                args[key] = val
        elif len(clear_components) == 2:
            return "Error: ", "No keys or values were passed"

        return command, args

    async def output_data(self, addr, message: str) -> str:
        command, args = await self.correct_command_and_args(message)
        dict_args = self.commands_dict[command].__annotations__
        if "Error" in command:
            return command + args + "\n"

        elif await self.check_args(command, args, dict_args):
            if "addr" in dict_args:
                result = await self.commands_dict[command](addr, **args)
            else:
                try:
                    result = await self.commands_dict[command](**args)
                except TypeError:
                    return "Error: check type hint for addr"

            if result is None:
                return "ok\n"
            else:
                return str(result) + "\n"

        else:
            return "Wrong arguments ot command\n"

    async def command_handler(self, reader, writer):
        data = await reader.readline()
        addr = writer.get_extra_info('peername')
        self.clients[addr] = writer
        while data:
            message = data.decode()
            send_data = await self.output_data(addr, message)
            print(f"Received {message!r} from {addr!r}")
            print(f"Send: {send_data!r}")
            writer.write(send_data.encode())
            await writer.drain()
            data = await reader.readline()

        print(f"Close the connection {addr!r}")
        del self.clients[addr]
        writer.close()

    async def run(self):
        server = await asyncio.start_server(self.command_handler, self.address, self.port)

        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        print(f'Serving on {addrs}')

        async with server:
            await server.serve_forever()
