import asyncio

from pyensign.ensign import Ensign

class SteamSubscriber:
    """
    SteamSubscriber queries the SteamPublisher for events.
    """
   
    def __init__(self) -> None:
        self.topic = "steam"
        self.ensign = Ensign()

    def run(self):
        """
        Run the subscriber forever.
        """
        asyncio.get_event_loop().run_until_complete(self.subscribe())

    async def subscribe(self):
        """
        Subscribe to SteamPublisher events from Ensign
        """

        # Get the topic ID from the topic name.
        topic_id = await self.ensign.topic_id(self.topic)

        # Subscribe to the topic.
        await self.ensign.subscribe(topic_id, on_event=print)
        # create a Future and await its result - this will ensure that the
        # subscriber will run forever since nothing in the code is setting the
        # result of the Future
        await asyncio.Future()

    
if __name__ == "__main__":
    subscriber = SteamSubscriber()
    subscriber.run()