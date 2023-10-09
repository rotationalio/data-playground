import os
import json
import asyncio

import numpy as np
from pyensign.ensign import Ensign

################################################################
# EarthquakeAnalyzer Class Methods
################################################################

class EarthquakeAnalyzer:
    """
    EarthquakeAnalyzer reads historic data off of an Ensign stream.
    """

    def __init__(self, topic="earthquakes-json"):
        """
        Initialize the EarthquakeAnalyzer, which use EnSQL to query
        historic data off the topic, and can produce an aggregate analysis
        given a user-provided window of time.

        Parameters
        ----------
        topic : string, default: "earthquakes-json"
            The name of the topic you wish to subscribe to.
        """
        self.topic = topic
        keys = self._load_keys()
        self.ensign = Ensign(
            client_id=keys["ClientID"],
            client_secret=keys["ClientSecret"]
        )

    def _load_keys(self):
        try:
            f = open(os.path.join("..", "client.json"))
            return json.load(f)
        except Exception as e:
            raise OSError(f"unable to load Ensign API keys from file: ", e)

    async def replay(self, slice=False, sample_size=100):
        """
        Replay all events, from the beginning. Use optional `slice` and
        `sample_size` params to extract a slice of data

        Parameters
        ----------
        slice : boolean, default=False
            Specify True if you want a small slice of data. Else leave false to get
            all historical data.

        sample_size : int, default=100
            If slice is True, the number of events to slice from the beginning of the
            event stream. If slice is False, this parameter is ignored.
        """
        if slice:
            q = f"SELECT * FROM {self.topic} LIMIT {str(sample_size)}"
        else:
            q = f"SELECT * FROM {self.topic}"

        # Get the cursor first!!
        cursor = await self.ensign.query(q)

        # The cursor is the async generator, so asynchronously process the events
        async for event in cursor:
            yield event

    def unpack(self, event):
        """
        Decode and ack the event.
        """
        try:
            data = json.loads(event.data)
        except json.JSONDecodeError:
            print("Received invalid JSON in event payload:", event.data)
            return

        return data

################################################################
# Helper Methods
################################################################

async def test_replay():
    m = EarthquakeAnalyzer()
    async for e in m.replay():
        print(e)

def update_avg(window):
    """
    Update the running average based on a sliding window of values
    provided as an argument
    """
    n = len(window)
    return np.convolve(window, np.ones(n)/n, mode="valid")[0]

async def analyze():
    """
    Get an average magnitude
    """
    window = [0.0, 0.0, 0.0, 0.0, 0.0]
    m = EarthquakeAnalyzer()
    async for e in m.replay(slice=False):
        jsn = m.unpack(e)
        new = jsn["magnitude"]
        window.append(float(new))
        window.pop(0)
        print(f"New magnitude reading: {new}")
        print(f"Experimental window is: {window}")
        print(f"Running average is: {update_avg(window)}")
        print()

if __name__ == "__main__":

    # asyncio.run(test_replay())

    asyncio.run(analyze())
