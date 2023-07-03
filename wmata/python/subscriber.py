import json
import asyncio
import warnings

from pyensign.ensign import Ensign
from pyensign.api.v1beta1.ensign_pb2 import Nack

# TODO Python>3.10 needs to ignore DeprecationWarning: There is no current event loop
warnings.filterwarnings("ignore")


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

        print("New metro report received:", data)
        await event.ack()

    async def subscribe(self):
        """
        Subscribe to the metro topic and parse the events.
        """
        id = await self.ensign.topic_id(self.topic)
        await self.ensign.subscribe(id, on_event=self.handle_event)
        await asyncio.Future()


if __name__ == "__main__":
    subscriber = MetroSubscriber()
    subscriber.run()
