# Accessing Real-time Metro Updates with Python

Washington DC's partly underground metro line (WMATA or "wuh-mah-tah"), is famously not the U-Bahn 😂 If you want to know when you train will really arrive, you need this feed!

Metro interruptions are also a great way to model complex systems, so this feed can also be integrated with other feeds (like [weather](https://github.com/rotationalio/data-playground/tree/main/weather/python)), to build a more complete picture of the interactions between the natural world and the human-made world.

## Getting Started

Ready to tap in to the stream? Let's do it!

### Install the Dependencies

```bash
git clone git@github.com:rotationalio/data-playground.git
cd data-playground/wmata/python
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

- Sign up for a [developer account at WMATA](https://developer.wmata.com/).
- Go to the PRODUCTS page and select the Default Tier, which is rate-limited to 10 calls/second and 50,000 calls per day.
- Subscribe to the Default Tier
- Copy your primary key into your bash profile: `export WMATA_KEY=<your-key>`
- `source` your bash profile in your current terminal window so that you can access your API key as an environment variable

If you're looking for more details about the DC Metro API, including how to interpret the data that comes back from API calls, check out their [docs](https://developer.wmata.com/docs/services/).


### Start the Subscriber
I know it sounds weird to start the subscriber first, but that's asynchronous programming for you!

```python subscriber.py```

You'll see it wait for you:

```bash
yrcomputersnickname:python YOURNAMEHERE$ python subscriber.py


```

### Start the Publisher

In a second window, run the publisher:

```python publisher.py```

You'll see acks start to come in:

```bash
yrcomputersnickname:python YOURNAMEHERE$ python publisher.py
Event committed at 2023-07-03 13:58:23.209736
Event committed at 2023-07-03 13:58:23.209773
Event committed at 2023-07-03 13:58:23.209777
Event committed at 2023-07-03 13:58:23.212564
Event committed at 2023-07-03 13:58:23.212583
...
```

And in your subscriber terminal, you'll see the data:

```bash
yrcomputersnickname:python YOURNAMEHERE$ python subscriber.py
New metro report received: {'incident_id': '001E815C-4A62-47EE-843D-5F0B788C799C', 'incident_type': 'Alert', 'routes_affected': ['P12'], 'description': 'Due to an accident at Addison Rd Station, buses may experience delays.', 'date_updated': '2023-07-03T13:43:14'}
New metro report received: {'incident_id': '38102CBA-04FA-4D88-B9B8-41E9D2549C73', 'incident_type': 'Alert', 'routes_affected': ['32'], 'description': 'Due to an accident on Pennsylvania Ave SE at 6th St, buses may experience delays.', 'date_updated': '2023-07-03T13:20:19'}
New metro report received: {'incident_id': '03EF58CA-4C96-477B-B0F8-E0B5EA2179D5', 'incident_type': 'Alert', 'routes_affected': ['32', '33', '36'], 'description': 'Buses are detouring, due to the DC 4th of July Celebration. More info at \nhttps://buseta.wmata.com', 'date_updated': '2023-07-03T06:15:34'}
New metro report received: {'incident_id': 'C83592B3-8399-4426-8568-FFCA1E5B3D9D', 'incident_type': 'Alert', 'routes_affected': ['W4'], 'description': 'Due to a mechanical issue at Anacostia Station on the W4 route, buses may experience delays.', 'date_updated': '2023-07-03T13:07:18'}
New metro report received: {'incident_id': '7B640278-9219-430F-A59C-81C5F7BDE5EA', 'incident_type': 'Alert', 'routes_affected': ['F4'], 'description': 'Due to a mechanical issue on Riggs Rd at East West Hwy on the F4 Route, buses are experiencing delays.', 'date_updated': '2023-07-03T12:18:34'}
...
```