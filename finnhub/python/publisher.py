import asyncio
import json
import os

import websockets

from pyensign.events import Event
from pyensign.ensign import Ensign
from utils import handle_ack, handle_nack


class TradesPublisher:
    """
    TradesPublisher queries an API for trading updates and publishes events to Ensign.
    """

    def __init__(self, symbols=["AAPL", "MSFT", "AMZN"], topic="trades",ensign_creds=''):
        self.symbols = symbols
        self.topic = topic
        self.ensign = Ensign(cred_path=ensign_creds)

    def run(self):
        """
        Run the publisher forever.
        """
        # Load finnhub API key from environment variable.
        token = os.environ.get('FINNHUB_API_KEY')
        if token is None:
            raise ValueError("FINNHUB_API_KEY environment variable not set.")

        # Run the publisher.
        asyncio.run(self.recv_and_publish(f"wss://ws.finnhub.io?token={token}"))

    async def recv_and_publish(self, uri):
        """
        Receive messages from the websocket and publish events to Ensign.
        """
        topic_id = await self.ensign.topic_id(self.topic)
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    for symbol in self.symbols:
                        await websocket.send(f'{{"type":"subscribe","symbol":"{symbol}"}}')

                    while True:
                        message = await websocket.recv()
                        for event in self.message_to_events(json.loads(message)):
                            await self.ensign.publish(topic_id, event, on_ack=handle_ack, on_nack=handle_nack)
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"Websocket connection closed: {e}")
                await asyncio.sleep(1)

    def message_to_events(self, message):
        """
        Convert a message from the Finnhub API to multiple Ensign events.
        """

        message_type = message["type"]
        if message_type == "ping":
            return
        elif message_type == "trade":
            for trade in message["data"]:
                data = {
                    "price": trade["p"],
                    "symbol": trade["s"],
                    "timestamp": trade["t"],
                    "volume": trade["v"]
                }
                yield Event(json.dumps(data).encode("utf-8"), mimetype="application/json")
        else:
            raise ValueError(f"Unknown message type: {message_type}")

if __name__ == "__main__":
    publisher = TradesPublisher(ensign_creds='secret/ensign_publisher.json')
    publisher.run()