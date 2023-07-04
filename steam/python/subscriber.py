import json
import asyncio
import warnings

from pyensign.ensign import Ensign
from pyensign.api.v1beta1.ensign_pb2 import Nack


# TODO Python>3.10 needs to ignore DeprecationWarning: There is no current event loop
warnings.filterwarnings("ignore")

class SteamSubscriber:
    """
    SteamSubscriber queries the SteamPublisher for events.
    """

    def __init__(self, topic="steam-stats-json"):
        """
        Parameters
        ----------
        topic : string, default: "steam-stats-json"
            The name of the topic you wish to publish to. If the topic doesn't yet
            exist, Ensign will create it for you. Tips on topic naming conventions can
            be found at https://ensign.rotational.dev/getting-started/topics/
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

        print("New steam report received:", data)
        await event.ack()

    async def subscribe(self):
        """
        Subscribe to SteamPublisher events from Ensign
        """
        id = await self.ensign.topic_id(self.topic)
        await self.ensign.subscribe(id, on_event=self.handle_event)
        await asyncio.Future()


if __name__ == "__main__":
    subscriber = SteamSubscriber()
    subscriber.run()