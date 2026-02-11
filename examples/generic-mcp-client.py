"""
Generic MCP Client for TrustScore

This script demonstrates how to connect to a TrustScore MCP endpoint using Python.
It handles basic WebSocket communication for model context protocol (MCP).
"""
import asyncio
import websockets
import json

async def connect_to_mcp(endpoint, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    async with websockets.connect(endpoint, extra_headers=headers) as websocket:
        # Send initial context request
        request = {
            "type": "context_request",
            "model": "trustscore-v1",
            "context": {
                "text": "Sample text for analysis",
                "metadata": {"source": "user_input"}
            }
        }
        await websocket.send(json.dumps(request))
        
        # Receive response
        response = await websocket.recv()
        data = json.loads(response)
        print(f"Received TrustScore: {data.get('score', 'N/A')}")
        print(f"Analysis: {data.get('analysis', 'No analysis provided')}")

# Example usage
if __name__ == "__main__":
    ENDPOINT = "wss://your-trustscore-server:port/mcp"
    API_KEY = "your-api-key-here"
    asyncio.run(connect_to_mcp(ENDPOINT, API_KEY))
