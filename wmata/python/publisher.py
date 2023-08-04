import os
import json
import asyncio
import warnings
from datetime import datetime, timedelta

import requests
from pyensign.events import Event
from pyensign.ensign import Ensign

# TODO Python>3.10 needs to ignore DeprecationWarning: There is no current event loop
warnings.filterwarnings("ignore")

# TODO: replace with YOU - your email and app details :)
ME = "(https://rotational.io/data-playground/dc-metro, wmata@rotational.io)"


class MetroPublisher:
    """
    MetroPublisher queries the WMATA API for public transportation data such as
    real-time bus and rail predictions.
    """

    def __init__(self, topic="metro-updates-json", wmata_key=None, interval=900, user=ME):
        """
        Parameters
        ----------
        topic : string, default: "metro-updates-json"
            The name of the topic you wish to publish to. If the topic doesn't yet
            exist, Ensign will create it for you. Tips on topic naming conventions can
            be found at https://ensign.rotational.dev/getting-started/topics/

        wmata_key : string, default: None
            You can put your API key for the WMATA Developer API here. If you leave it
            blank, the publisher will attempt to read it from your environment variables

        interval : int, default: 900
            The number of seconds to wait between API calls so we don't irritate the
            nice people at WMATA.

        user : str
            When querying the WMATA API, as a courtesy, they like you to identify your
            app and contact info (aka User Agent details)
        """
        self.topic = topic
        self.interval = interval
        self.datatype = "application/json"
        self.url = "https://api.wmata.com/Incidents.svc/json/BusIncidents"

        if wmata_key is None:
            self.wmata_key = os.getenv("WMATA_KEY")
        else:
            self.wmata_key = wmata_key

        if self.wmata_key is None:
            raise Exception("no WMATA key found; see README section on API key setup")

        self.header = {
            "User-Agent": user,
            "api_key": self.wmata_key
        }

        # NOTE: If you need an Ensign client_id & client_secret, register for a free
        # account at: https://rotational.app/register

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
        ts = datetime.fromtimestamp(
            ack.committed.seconds + ack.committed.nanos / 1e9)
        print(f"Event committed at {ts}")

    async def print_nack(self, nack):
        """
        Enable the Ensign server to notify the Publisher the event has NOT been
        acknowledged

        This is optional for you, but can be very helpful for communication in
        asynchronous contexts!
        """
        print(f"Event was not committed with error {nack.code}: {nack.error}")

    def unpack_wmata_response(self, message):
        """
        Convert a message from the WMATA API to potentially multiple Ensign events,
        and yield each.

        Parameters
        ----------
        message : dict
            JSON formatted response from the WMATA API containing metro details
        """
        metro_events = message.get("BusIncidents", None)
        if metro_events is None:
            raise Exception(
                "unexpected response from wmata request, no metro events found")

        for metro_event in metro_events:
            data = {
                "incident_id": metro_event.get("IncidentID", None),
                "incident_type": metro_event.get("IncidentType", None),
                "routes_affected": metro_event.get("RoutesAffected", None),
                "description": metro_event.get("Description", None),
                "date_updated": metro_event.get("DateUpdated", None),
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
            # query = self.compose_query()
            response = requests.get(self.url, headers=self.header).json()

            # unpack the API response and parse it into events
            events = self.unpack_wmata_response(response)
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
        asyncio.get_event_loop().run_until_complete(self.recv_and_publish())


if __name__ == "__main__":
    publisher = MetroPublisher()
    publisher.run()
