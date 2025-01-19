import asyncio
import websockets
import unittest

HOSTNAME = 'localhost'
PORT = 8765

class TestWebSocketConnection(unittest.TestCase):
    async def connect_to_server(self):
        uri = f"ws://{HOSTNAME}:{PORT}"  # Replace with your WebSocket server URI
        async with websockets.connect(uri) as websocket, asyncio.timeout(1):
            response = await websocket.recv()
            return response

    def test_websocket_connection(self):
        response = asyncio.get_event_loop().run_until_complete(self.connect_to_server())
        self.assertEqual(response, "Hello, Client!")  # Replace with the expected response from your server

    def test_send_action(self):
        async def send_action():
            uri = f"ws://{HOSTNAME}:{PORT}"
            async with websockets.connect(uri) as websocket, asyncio.timeout(1):
                await websocket.recv()
                await websocket.send('{"type": "action", "action": "left"}')
                response = await websocket.recv()
                return response
            
        response = asyncio.get_event_loop().run_until_complete(send_action())
        self.assertEqual(response, "Action received: move")

if __name__ == "__main__":
    unittest.main()