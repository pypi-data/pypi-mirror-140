import asyncio
import re


async def correct_command_and_args(message: str) -> tuple:
    result = {}
    # first component of command second keys third values
    message_components = re.split(" --key | --val ", message)
    if len(message_components) != 3:
        return "Error: ", "No keys or values were passed"
    command = message_components[0]
    keys, vals = message_components[1].split(), message_components[2].split()

    if len(keys) != len(vals):
        return "Error: ", f"The number of keys differs from the arguments keys: {len(keys)}, vals: {len(vals)}"

    for key, val in zip(keys, vals):
        result[key] = val

    return command, result


class MySocketLib:
    def __init__(self, address: str, port: int):
        self.address = address
        self.port = port
        self.commands_dict = dict()

    def command(self, func: callable) -> callable:
        self.commands_dict[func.__name__] = func

        async def inner(*args, **kwargs) -> callable:
            return await func(*args, **kwargs)

        return inner

    async def check_args(self, command: str, args: dict) -> bool:
        try:
            dict_args = self.commands_dict[command].__annotations__
        except KeyError:
            return False

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

    async def output_data(self, message: str) -> str:
        command, args = await correct_command_and_args(message)
        if "Error" in command:
            return command + args + "\n"
        elif await self.check_args(command, args):
            result = await self.commands_dict[command](**args)
            if result is None:
                return "ok\n"
            else:
                return str(result) + "\n"
        else:
            return "Wrong arguments ot command\n"

    async def command_handler(self, reader, writer):
        data = await reader.readline()
        while data:
            message = data.decode()
            addr = writer.get_extra_info('peername')
            send_data = await self.output_data(message)
            print(f"Received {message!r} from {addr!r}")
            print(f"Send: {send_data!r}")
            writer.write(send_data.encode())
            await writer.drain()
            data = await reader.readline()

        print("Close the connection")
        writer.close()

    async def run(self):
        server = await asyncio.start_server(self.command_handler, self.address, self.port)

        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        print(f'Serving on {addrs}')

        async with server:
            await server.serve_forever()
