import json
import asyncio

from pyensign.ensign import Ensign
from pyensign.api.v1beta1.ensign_pb2 import Nack


class FlightsSubscriber:
    def __init__(self, topic="flight-positions", ensign_creds=""):
        self.topic = topic
        self.ensign = Ensign(cred_path=ensign_creds)

    def run(self):
        """
        Run the subscriber forever.
        """
        asyncio.get_event_loop().run_until_complete(self.subscribe())

    async def handle_event(self, event):
        """
        Decode and ack the event.
        """
        try:
            data = json.loads(event.data)
        except json.JSONDecodeError:
            print("Received invalid JSON in event payload:", event.data)
            await event.nack(Nack.Code.UNKNOWN_TYPE)
            return

        print("Received flight position:", data)
        await event.ack()

    async def subscribe(self):
        """
        Subscribe to the flight positions topic and parse the events.
        """
        id = await self.ensign.topic_id(self.topic)
        await self.ensign.subscribe(id, on_event=self.handle_event)
        await asyncio.Future()


if __name__ == "__main__":
    subscriber = FlightsSubscriber()
    subscriber.run()
