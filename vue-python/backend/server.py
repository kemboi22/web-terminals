import asyncio
import json
import os
import pty
import platform
import websockets
import sys
import threading

ptys = {}

HOST = "0.0.0.0"
PORT = 8765


async def handle_client(websocket):
    client = websocket.remote_address
    print(f"[+] Connection opened from {client}")

    pid, fd = pty.fork()

    if pid == 0:
        shell = "bash"
        os.execvp(shell, [shell])

    ptys[websocket] = (fd, pid)

    loop = asyncio.get_event_loop()

    def read_pty():
        while True:
            try:
                data = os.read(fd, 1024)
                asyncio.run_coroutine_threadsafe(
                    websocket.send(
                        json.dumps(
                            {"type": "data", "data": data.decode(errors="ignore")}
                        )
                    ),
                    loop,
                )
            except:
                break

    threading.Thread(target=read_pty, daemon=True).start()

    try:
        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "command":
                os.write(fd, data["data"].encode())

    except websockets.exceptions.ConnectionClosed:
        pass

    finally:
        print(f"[-] Connection closed from {client}")
        os.close(fd)
        os.kill(pid, 9)
        del ptys[websocket]


def print_banner():
    print("=" * 50)
    print(" WebSocket Terminal Server")
    print("=" * 50)
    print(f"Python Version : {sys.version.split()[0]}")
    print(f"OS             : {platform.system()} {platform.release()}")
    print(f"Server URL     : ws://localhost:{PORT}")
    print("=" * 50)


async def main():
    print_banner()
    async with websockets.serve(handle_client, HOST, PORT):
        await asyncio.Future()


asyncio.run(main())
