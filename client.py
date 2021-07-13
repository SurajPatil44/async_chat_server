import contextlib
from chat_stream import split_lines,handle_write
import asyncio
import aiofiles.threadpool
import sys


async def handle_reads(reader):
    async for message in split_lines(reader,b"\r\n"):
        text = message.decode()
        print(f"Recieved {text!r}")
        if text == "quit":
            break

async def stream_to_queue(file,queue):
    loop = asyncio.get_event_loop()
    async for message in aiofiles.threadpool.wrap(file,loop=loop):
        if message.endswith("\n"):
            message = message.replace("\n","\r\n")
        await queue.put(message.encode())

async def send_file(file):
    try:
        write_q = asyncio.Queue()
        reader,writer = await asyncio.open_connection("127.0.0.1",8888)
        read_handler = asyncio.create_task(handle_reads(reader))
        write_handler = asyncio.create_task(handle_write(writer,write_q))
        copy_handler = asyncio.create_task(stream_to_queue(file,write_q))
        done,pending = await asyncio.wait(
                [read_handler,write_handler,copy_handler], return_when=asyncio.FIRST_COMPLETED
        )
        #print(done)
        for task in pending:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
    except Exception as exc:
        print(f"exception is {exc}")

if __name__ == "__main__":
    try:
        asyncio.run(send_file(sys.stdin))
    except KeyboardInterrupt:
        sys.exit(0)
