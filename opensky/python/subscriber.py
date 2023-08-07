import json
import asyncio

from pyensign.ensign import Ensign
from pyensign.api.v1beta1.ensign_pb2 import Nack


class FlightsSubscriber:
    """
    FlightsSubscriber consumes flight vector events from Ensign.
    """

    def __init__(self, topic="flight-vectors", ensign_creds=""):
        """
        Create a FlightsSubscriber to consume flight vector events from an Ensign
        topic. Nothing will be consumed until run() is called.

        Parameters
        ----------
        topic : str (default: "flight-vectors")
            The name of the topic to consume from.

        ensign_creds : str (optional)
            The path to your Ensign credentials file. If not provided, credentials will
            be read from the ENSIGN_CLIENT_ID and ENSIGN_CLIENT_SECRET environment
            variables.
        """
        self.topic = topic
        self.ensign = Ensign(cred_path=ensign_creds)

    def run(self):
        """
        Run the subscriber forever.
        """
        asyncio.run(self.subscribe())

    async def handle_event(self, event):
        """
        Decode and ack the event back to Ensign.
        """
        try:
            data = json.loads(event.data)
        except json.JSONDecodeError:
            print("Received invalid JSON in event payload:", event.data)
            await event.nack(Nack.Code.UNKNOWN_TYPE)
            return

        print("Received flight vector:", data)
        await event.ack()

    async def subscribe(self):
        """
        Subscribe to the flight vectors topic and parse the events.
        """
        id = await self.ensign.topic_id(self.topic)
        async for event in self.ensign.subscribe(id):
            await self.handle_event(event)


if __name__ == "__main__":
    subscriber = FlightsSubscriber(ensign_creds="secret/subscribe_creds.json")
    subscriber.run()
