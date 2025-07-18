import asyncio
import json
import threading
import websockets

class WebSocketServer:
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.loop = asyncio.new_event_loop()
        self.server = None
        self._thread = None

    def start(self):
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def send_spell(self, spell: str, gesture: str):
        if not self.clients:
            return
        payload = {
            "type": "spell",
            "spell": spell,
            "gesture": gesture,
        }
        message = json.dumps(payload)
        asyncio.run_coroutine_threadsafe(self._broadcast(message), self.loop)

    async def _handler(self, websocket):
        print("[WebSocket] Client connected.")
        self.clients.add(websocket)
        try:
            await websocket.send(json.dumps({
                "type": "hello",
                "from": "gesture_server",
                "version": "0.1"
            }))
            async for msg in websocket:
                print(f"[WebSocket] Received from client: {msg}")
        except Exception as e:
            print(f"[WebSocket] Handler error: {e}")
        finally:
            self.clients.discard(websocket)
            print("[WebSocket] Client disconnected.")

    async def _broadcast(self, message: str):
        dead = []
        for ws in list(self.clients):
            try:
                await ws.send(message)
            except Exception as e:
                print(f"[WebSocket] Send error: {e}")
                dead.append(ws)
        for ws in dead:
            self.clients.discard(ws)

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._start_server())
        print(f"[WebSocket] Server started on ws://{self.host}:{self.port}")
        try:
            self.loop.run_forever()
        finally:
            self.loop.run_until_complete(self._stop_server())
            self.loop.close()

    async def _start_server(self):
        self.server = await websockets.serve(self._handler, self.host, self.port)

    async def _stop_server(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
