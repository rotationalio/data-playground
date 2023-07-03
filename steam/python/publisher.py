import asyncio
import requests
import json
import os

from datetime import datetime
from pyensign.events import Event
from pyensign.ensign import Ensign

class SteamPublisher:
    """
    SteamPublisher queries the steam API and publishes events to Ensign.
    """
    topic="steam"

    def __init__(self, topic="") -> None:
        if topic != "":
            self.topic = topic
        self.ensign = Ensign()

    def run(self):
        """
        Run the steam publisher forever.
        """
        self.key = os.environ.get("STEAM_API_KEY")
        if self.key is None:
            raise ValueError("STEAM_API_KEY environment variable must be set.")        
        self.gameList = json.loads(requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/").content)["applist"]["apps"]
        asyncio.get_event_loop().run_until_complete(self.recv_and_publish())

    async def recv_and_publish(self):
        topic_id = await self.ensign.topic_id(self.topic)
        while True:
            try:
                # Retrieve the player count for the current game/appid
                response = requests.get(f"http://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={self.gameList[i]}")
                response = json.loads(response.content) 
                
                # Convert the response to an event and publish it
                for event in self.createEvents(response, i):
                    await self.ensign.publish(topic_id, event, on_ack=self.handle_ack, on_nack=self.handle_nack)
                    await asyncio.sleep(1)
            except Exception as e:
                print(f"error: {e}")
                await asyncio.sleep(1)

    def createEvents(self, response, i):
        gameName = self.gameList[i]["name"]
        if gameName == '':
            gameName = "N/A"
        data = {"game": gameName, 
                "id": self.gameList[i]["appid"], 
                "count": response["response"]["player_count"]}
        print(data)
        event = Event(json.dumps(data).encode("utf-8"), mimetype="application/json")
        yield event

    async def handle_ack(self, ack):
        ts = datetime.fromtimestamp(ack.committed.seconds + ack.committed.nanos / 1e9)
        print(f"Event committed at {ts}")

    async def handle_nack(self, nack):
        print(f"Could not commit event {nack.id} with error {nack.code}: {nack.error}")

if __name__ == "__main__":
    publisher = SteamPublisher("steam")
    publisher.run()
