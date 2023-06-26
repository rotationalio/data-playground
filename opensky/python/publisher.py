import json
import asyncio
from datetime import datetime

from aiohttp import ClientSession, BasicAuth
from pyensign.events import Event
from pyensign.ensign import Ensign
from python_opensky import OpenSky, BoundingBox


class FlightsPublisher:
    def __init__(
        self,
        topic="flight-positions",
        ensign_creds="",
        opensky_creds="secret/opensky.json",
        min_latitude=-66,
        max_latitude=49,
        min_longitude=-124,
        max_longitude=24,
        interval=60,
    ):
        self.topic = topic
        self.bounding_box = BoundingBox(
            min_latitude=min_latitude,
            max_latitude=max_latitude,
            min_longitude=min_longitude,
            max_longitude=max_longitude,
        )
        self.interval = interval
        self.ensign = Ensign(cred_path=ensign_creds)
        with open(opensky_creds) as f:
            self.opensky_creds = json.load(f)
            if (
                "username" not in self.opensky_creds
                or "password" not in self.opensky_creds
            ):
                raise ValueError(
                    "Opensky credentials must contain both username and password"
                )

    def run(self):
        """
        Run the publisher forever.
        """
        asyncio.get_event_loop().run_until_complete(self.recv_and_publish())

    async def print_ack(self, ack):
        ts = datetime.fromtimestamp(ack.committed.seconds + ack.committed.nanos / 1e9)
        print(f"Event committed at {ts}")

    async def print_nack(nack):
        print(f"Event was not committed with error {nack.code}: {nack.error}")

    async def recv_and_publish(self):
        """
        Retrieve flight data from OpenSky and publish events to Ensign.
        """
        await self.ensign.ensure_topic_exists(self.topic)

        async with ClientSession() as session:
            async with OpenSky(session=session) as opensky:
                opensky.authenticate(
                    BasicAuth(
                        login=self.opensky_creds["username"],
                        password=self.opensky_creds["password"],
                    )
                )

                while True:
                    try:
                        states = await opensky.get_states(
                            bounding_box=self.bounding_box
                        )
                    except Exception as e:
                        print(e)
                        await asyncio.sleep(self.interval)
                        continue
                    for event in self.states_to_events(states):
                        await self.ensign.publish(
                            self.topic,
                            event,
                            on_ack=self.print_ack,
                            on_nack=self.print_nack,
                        )

                    await asyncio.sleep(self.interval)

    def states_to_events(self, states):
        for vector in states.states:
            data = {
                "icao24": vector.icao24,
                "callsign": vector.callsign,
                "origin_country": vector.origin_country,
                "time_position": vector.time_position,
                "last_contact": vector.last_contact,
                "longitude": vector.longitude,
                "latitude": vector.latitude,
                "geo_altitude": vector.geo_altitude,
                "on_ground": vector.on_ground,
                "velocity": vector.velocity,
                "true_track": vector.true_track,
                "vertical_rate": vector.vertical_rate,
                "sensors": vector.sensors,
                "barometric_altitude": vector.barometric_altitude,
                "transponder_code": vector.transponder_code,
                "special_purpose_indicator": vector.special_purpose_indicator,
                "position_source": vector.position_source,
                "category": vector.category,
            }
            yield Event(
                data=json.dumps(data).encode("utf-8"), mimetype="application/json"
            )
            return


if __name__ == "__main__":
    publisher = FlightsPublisher()
    publisher.run()
