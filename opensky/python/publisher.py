import json
import asyncio
import warnings
from datetime import datetime

from aiohttp import ClientSession, BasicAuth

from pyensign.events import Event
from pyensign.ensign import Ensign
from python_opensky import OpenSky, BoundingBox

# TODO: Python>=3.10 raises a DeprecationWarning: There is no current event loop. We need to fix this in PyEnsign!
warnings.filterwarnings("ignore", category=DeprecationWarning)


class FlightsPublisher:
    """
    FlightsPublisher queries the OpenSky API for real-time flight data and publishes
    flight vector events to Ensign.
    """

    def __init__(
        self,
        topic="flight-vectors",
        ensign_creds="",
        opensky_creds="secret/opensky.json",
        min_latitude=-66,
        max_latitude=49,
        min_longitude=-124,
        max_longitude=24,
        interval=60,
    ):
        """
        Create a FlightsPublisher to publish flight vectors to an Ensign topic. Nothing
        will be published until run() is called.

        Parameters
        ----------
        topic : str (default: "flight-vectors")
            The name of the topic to publish to.

        ensign_creds : str (optional)
            The path to your Ensign credentials file. If not provided, credentials will
            be read from the ENSIGN_CLIENT_ID and ENSIGN_CLIENT_SECRET environment
            variables.

        opensky_creds : str (default: "secret/opensky.json")
            The path to your OpenSky credentials file. The credentials file must be a
            JSON file with both a "username" and "password" field.

        min_latitude : float (default: -66)
            The minimum latitude of the bounding box to query for flight vectors.

        max_latitude : float (default: 49)
            The maximum latitude of the bounding box to query for flight vectors.

        min_longitude : float (default: -124)
            The minimum longitude of the bounding box to query for flight vectors.

        max_longitude : float (default: 24)
            The maximum longitude of the bounding box to query for flight vectors.

        interval : int (default: 60)
            The number of seconds to wait between queries to the OpenSky API.
        """
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
                    "OpenSky credentials must contain both username and password"
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
                    # Call the OpenSky API to get a set of flight vectors in the
                    # bounding box.
                    try:
                        response = await opensky.get_states(
                            bounding_box=self.bounding_box
                        )
                    except Exception as e:
                        print(e)
                        await asyncio.sleep(self.interval)
                        continue

                    # Publish each flight vector to Ensign.
                    for event in self.vectors_to_events(response.states):
                        await self.ensign.publish(
                            self.topic,
                            event,
                            on_ack=self.print_ack,
                            on_nack=self.print_nack,
                        )

                    await asyncio.sleep(self.interval)

    def vectors_to_events(self, vectors):
        """
        Convert state vectors to Ensign events. This is a generator function that
        returns the events one at a time.
        """
        for vector in vectors:
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


if __name__ == "__main__":
    publisher = FlightsPublisher(ensign_creds="secret/ensign.json")
    publisher.run()
