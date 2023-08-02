import json
import asyncio
from datetime import datetime, timedelta

import requests
from pyensign.events import Event
from pyensign.ensign import Ensign

# TODO: replace with YOU - your email and app details :)
ME = "(https://rotational.io/data-playground/us-geological, earthquakes@rotational.io)"


class EarthquakePublisher:
    """
    EarthquakePublisher queries the USGS API for natural disaster updates and publishes them
    as events to Ensign.
    """

    def __init__(self, topic="earthquakes-json", interval=900, user=ME):
        """
        Parameters
        ----------
        topic : string, default: "earthquakes-json"
            The name of the topic you wish to publish to. If the topic doesn't yet
            exist, Ensign will create it for you. Tips on topic naming conventions can
            be found at https://ensign.rotational.dev/getting-started/topics/

        interval : int, default: 900
            The number of seconds to wait between API calls so we don't irritate the
            nice people at USGS.

        user : str
            When querying the USGS API, as a courtesy, they like you to identify your
            app and contact info (aka User Agent details)
        """
        self.topic = topic
        self.interval = interval
        self.url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        self.user = {"User-Agent": user}
        self.datatype = "application/json"

        # NOTE: If you need a client_id and client_secret, register for a free account
        # at: https://rotational.app/register

        # Start a connection to the Ensign server. If you do not supply connection
        # details, PyEnsign will read them from your environment variables.
        self.ensign = Ensign()

        # Alternatively you can supply `client_id` & `client_secret` as string args, eg
        # self.ensign = Ensign(client_id="your_client_id", client_secret="your_secret")

    async def print_ack(self, ack):
        """
        Enable the Ensign server to notify the Publisher the event has been acknowledged

        This is optional for you, but can be very helpful for communication in
        asynchronous contexts!
        """
        ts = datetime.fromtimestamp(ack.committed.seconds + ack.committed.nanos / 1e9)
        print(f"Event committed at {ts}")

    async def print_nack(self, nack):
        """
        Enable the Ensign server to notify the Publisher the event has NOT been
        acknowledged

        This is optional for you, but can be very helpful for communication in
        asynchronous contexts!
        """
        print(f"Event was not committed with error {nack.code}: {nack.error}")

    def compose_query(self):
        """
        Combine the base URI with the time-related query params
        Ask for only the data from the last 15 minutes

        NOTE: There are other query params you can leverage to reduce the total results.
        For example, you can add the `minmagnitude` param to only get results for bigger
        earthquakes. Check out the docs for more details:
        https://earthquake.usgs.gov/fdsnws/event/1/#parameters
        """
        start = datetime.now() - timedelta(hours=0, minutes=15)
        return self.url + "?format=geojson" + "&starttime=" + start.isoformat()

    def unpack_usgs_response(self, message):
        """
        Convert a message from the USGS API to potentially multiple Ensign events,
        and yield each.

        Parameters
        ----------
        message : dict
            JSON formatted response from the USGS API containing forecast details
        """
        geo_events = message.get("features", None)
        if geo_events is None:
            raise Exception(
                "unexpected response from usgs request, no geo-events found"
            )
        for geo_event in geo_events:
            details = geo_event.get("properties", None)
            if details is None:
                raise Exception(
                    "unable to parse usgs api response, no geo-event details found"
                )

            # There's a lot available! For this example, we'll just parse out a few
            # fields from the USGS API response:
            data = {
                "magnitude": details.get("mag", None),
                "place": details.get("place", None),
                "time": details.get("time", None),
                "updated": details.get("updated", None),
                "article_link": details.get("url", None),
                "type": details.get("type", None),
                "rms": details.get("rms", None),
                "gap": details.get("gap", None),
            }

            yield Event(json.dumps(data).encode("utf-8"), mimetype=self.datatype)

    async def recv_and_publish(self):
        """
        At some interval (`self.interval`), ping the API to get any newly updated
        events from the last interval period

        Publish report data to the `self.topic`
        """
        await self.ensign.ensure_topic_exists(self.topic)

        while True:
            query = self.compose_query()
            response = requests.get(query).json()

            # unpack the API response and parse it into events
            events = self.unpack_usgs_response(response)
            for event in events:
                await self.ensign.publish(
                    self.topic,
                    event,
                    on_ack=self.print_ack,
                    on_nack=self.print_nack,
                )

            # sleep for a bit before we ping the API again
            await asyncio.sleep(self.interval)

    def run(self):
        """
        Run the publisher forever.
        """
        asyncio.run(self.recv_and_publish())


if __name__ == "__main__":
    publisher = EarthquakePublisher()
    publisher.run()
