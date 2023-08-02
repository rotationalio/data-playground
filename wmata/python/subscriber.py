import json
import asyncio

from pyensign import nack
from pyensign.ensign import Ensign


class MetroSubscriber:
    """
    MetroSubscriber subscribes to an Ensign stream that the MetroPublisher is
    writing new metro reports to at some regular interval.
    """

    def __init__(self, topic="metro-updates-json"):
        """
        Initialize the MetroSubscriber, which will allow a data consumer to
        subscribe to the topic that the publisher is writing metro updates to

        Parameters
        ----------
        topic : string, default: "metro-updates-json"
            The name of the topic you wish to subscribe to.
        """
        self.topic = topic
        self.ensign = Ensign()

    def run(self):
        """
        Run the subscriber forever.
        """
        asyncio.run(self.subscribe())

    async def handle_event(self, event):
        """
        Decode and ack the event.
        """
        try:
            data = json.loads(event.data)
        except json.JSONDecodeError:
            print("Received invalid JSON in event payload:", event.data)
            await event.nack(nack.UnknownType)
            return

        print("New metro report received:", data)
        await event.ack()

    async def subscribe(self):
        """
        Subscribe to the metro topic and parse the events.
        """
        id = await self.ensign.topic_id(self.topic)
        async for event in self.ensign.subscribe(id):
            await self.handle_event(event)


if __name__ == "__main__":
    subscriber = MetroSubscriber()
    subscriber.run()
