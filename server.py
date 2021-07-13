import asyncio
import sys
import contextlib
from chat_stream import split_lines,write,handle_write

async def handle_connection(reader,writer):
    queue = asyncio.Queue()

    #def write_soon(message):
    #    todo.add(asyncio.create_task(write:(writer,message)))


    #write_soon(b"welcome.......!!!!!!")

    write_handler = asyncio.create_task(handle_write(writer,queue))

    ctx = {
        "addr" : str(writer.get_extra_info("peername")),
        "my_nick" : "",
    }

    try:
        await handle_command(reader,queue,ctx)

    finally:
        my_nick = ctx["my_nick"]
        if my_nick in users:
            del users[my_nick]
        await queue.put(b"")
        print("closing connection")
        with contextlib.suppress(asyncio.CancelledError):
            await write_handler

async def handle_command(reader,queue,ctx):
    try:
        addr = ctx["addr"]
        my_nick = ctx["my_nick"]
        await queue.put(b"welcome introduce yourself....!!!!")
        async for message in split_lines(reader,b"\r\n"):
            text = message.decode()
            print(f"got {text}")
            if text == "quit":
                await queue.put(message)
                break
            if text.startswith("I'm "):
                command,my_nick = text.split(" ",1)
                users[my_nick] = queue
                ctx["my_nick"] = my_nick
            elif text.startswith("@"):
                ##broadcast 
                if not my_nick:
                    await queue.put(b"introduce to send messages")
                    continue
                at_nick_and_message = text.split(" ",1)
                at_nick = at_nick_and_message[0]
                user_message = b""
                if len(at_nick_and_message) > 1:
                    user_message = at_nick_and_message[1]
                nick = at_nick[1:]
                print(f"current nick is {nick}")
                if nick == "all":
                    print(users.keys())
                    for key in users.keys():
                        if key != my_nick:
                            user_message = f"<{my_nick}>:{user_message}"
                            await users[key].put(user_message.encode())
                        else:
                            pass
                elif nick not in users:
                    await queue.put(b"unknwon users: "+ nick.encode())
                    continue
                else:
                    user_message = f"<{my_nick}>:{user_message}"
                    await users[nick].put(user_message.encode())
    except Exception as E:
        print(f"error {E} in handle_command")



async def main():
    server = await asyncio.start_server(handle_connection,"127.0.0.1",8888)
    addr = server.sockets[0].getsockname() if server.sockets else "unknown"
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        users = {}
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)


                
