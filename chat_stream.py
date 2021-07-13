import asyncio


async def handle_write(writer,queue):
    try:
        while True:
            bt = await queue.get() 
            #print(f"sending {bt}")
            if bt == b"":
                break
            await write(writer,bt)
    finally:
        await writer.drain()
        writer.close()
        
async def split_lines(reader,sentinel="\r\n"):
    data = bytearray()
    try:
        while True:
            data += await reader.read(100)
            if sentinel in data:
                message,data = data.split(sentinel,1)
                #print(f"recieved {message}")
                yield message
    except ConnectionResetError:
        pass
    if data:
        yield data

async def write(writer,message,sentinel=b"\r\n"):
    if not message.endswith(sentinel):
        message += sentinel
    writer.write(message)
    await writer.drain()
