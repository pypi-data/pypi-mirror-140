 ###Как использовать
 1. Установка
 
    
    pip install asyncio_tcp_messages_team_2

 2. Пример сервера. В начале объявляем класс MySocketLib с ip и портом.
     После чего регистрируем функций которые вам нужны, для регистраций 
     команды нужно указать декоратор @app.command 
    

    import asyncio

    from asyncio_tcp_messages.main import MySocketLib

    app = MySocketLib('127.0.0.1', 8889)

    ter = {}


    @app.command
    async def set_data(key: str, val: int):
        await ter[key] = val


    @app.command
    async def get_data(key: str):
        return ter[key]
    
    
    asyncio.run(app.run())

3. Пример клиента


    import asyncio
    
    
    async def tcp_client():
        reader, writer = await asyncio.open_connection('127.0.0.1', 8889)
    
        while True:
            message = input("Send: ") + "\n"
            if not message:
                break
            writer.write(message.encode())
            await writer.drain()
            data = await reader.readline()
            print(data.decode())
        print('Close the connection')
        writer.close()
    
    
    async def main():
        await asyncio.gather(tcp_client())
    
    
    if __name__ == '__main__':
        asyncio.run(main())     


4. Пример работы


    set_data --key key val --val 21 12
    >> ok
    get_data --key key --val 21
    >> 12