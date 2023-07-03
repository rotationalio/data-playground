# Accessing Real-time Earthquake Data with Python

Connect directly to the USGS API means having realtime access to important and life-saving data about natural disasters.

## Getting Started

Ready to save lives? Let's do it!

### Install the Dependencies

```bash
git clone git@github.com:rotationalio/data-playground.git
cd data-playground/earthquakes/python
pip install -r requirements.txt
```

### API Keys


You will need Ensign API keys, which you can get by registering for a [free Ensign account](https://rotational.app/register).

Create an [Ensign API key](https://rotational.app) with the permissions:

```
publisher
topics:create
topics:read
```

Alternatively, specify Ensign credentials in the environment.
```
$ export ENSIGN_CLIENT_ID=<your-client-id>
$ export ENSIGN_CLIENT_SECRET=<your-client-secret>
```

### API Details

If you're looking for more details about the USGS API, including how to interpret the data that comes back from API calls, check out their [docs](https://earthquake.usgs.gov/fdsnws/event/1/).

Insofar as rate-limiting goes, it doesn't look like there are any hard limits at the
time of this writing, but [they suggest](https://geohazards.usgs.gov/pipermail/realtime-feeds/2022-January/000028.html) not querying more frequently than every 60 seconds, as the results are cached for that long. It appears that 15 minute intervals is probably the best window.

### Start the Subscriber
I know it sounds weird to start the subscriber first, but that's asynchronous programming for you!

```python subscriber.py```

You'll see it wait for you:

```bash
yrcomputersnickname:weather YOURNAMEHERE$ python subscriber.py


```

### Start the Publisher

In a second window, run the publisher:

```python publisher.py```

You'll see acks start to come in:

```bash
yrcomputersnickname:python YOURNAMEHERE$ python publisher.py
Event committed at 2023-06-30 15:42:25.741311
Event committed at 2023-06-30 15:42:25.745165
Event committed at 2023-06-30 15:42:25.745179
Event committed at 2023-06-30 15:42:25.745183
...
```

And in your subscriber terminal, you'll see the data:

```bash
yrcomputersnickname:python YOURNAMEHERE$ python subscriber.py
New earthquake report received: {'magnitude': 1.8, 'place': '83 km NW of Karluk, Alaska', 'time': 1688153699651, 'updated': 1688153851807, 'article_link': 'https://earthquake.usgs.gov/earthquakes/eventpage/ak0238bnsgtv', 'type': 'earthquake', 'rms': 0.49, 'gap': None}
New earthquake report received: {'magnitude': 1.09, 'place': '4km ENE of Home Gardens, CA', 'time': 1688153196420, 'updated': 1688153416447, 'article_link': 'https://earthquake.usgs.gov/earthquakes/eventpage/ci40500808', 'type': 'earthquake', 'rms': 0.3, 'gap': 74}
New earthquake report received: {'magnitude': 1.21, 'place': '6 km ENE of Drumright, Oklahoma', 'time': 1688152513740, 'updated': 1688152999250, 'article_link': 'https://earthquake.usgs.gov/earthquakes/eventpage/ok2023msir', 'type': 'quarry blast', 'rms': 0.35, 'gap': 132}
New earthquake report received: {'magnitude': 2.47, 'place': '3 km WSW of La Parguera, Puerto Rico', 'time': 1688151658770, 'updated': 1688152327360, 'article_link': 'https://earthquake.usgs.gov/earthquakes/eventpage/pr71415303', 'type': 'earthquake', 'rms': 0.09, 'gap': 237}
...
```