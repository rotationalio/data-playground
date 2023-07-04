# Steam Python

Connect to the Steam API to get access to a list of steam games and their current player count.

## Setup

This example will use the `pyensign` package to create a publisher that will query and collect data from the Steam API, persisting it to a topic, and a subscriber that will read the data from the topic.

Install requirements

```bash
$ pip install -r requirements.txt
```

## API Key Setup

You will need a few API keys for this project.

### Steam API Keys

Get a [Steam API key](https://cran.r-project.org/web/packages/CSGo/vignettes/auth.html) from Steam.
**NOTE: To be granted access to the Steam API, you must first purchase at least 5 dollars (USD) in the Steam Store!**

Once you have obtained your key, store it as an environment variable.

```bash
$ export STEAM_API_KEY=<your-steam-api-key>
```

### Ensign API Keys
Create an [Ensign API key](https://rotational.app) with the permissions:

```bash
publisher
topics:create
topics:read
```

Alternatively, specify Ensign credentials in the environment.
```bash
$ export ENSIGN_CLIENT_ID=<your-client-id>
$ export ENSIGN_CLIENT_SECRET=<your-client-secret>
```

## Run the Publisher
In one terminal window, create a publisher and start publishing events with the following call:

```bash
$ python publisher.py
```

You should see some acks come back, indicating that events are being committed by Ensign.

```bash
Event committed at 2023-07-04 12:10:02.403597
Event committed at 2023-07-04 12:10:04.203062
Event committed at 2023-07-04 12:10:04.203089
Event committed at 2023-07-04 12:10:04.457769
Event committed at 2023-07-04 12:10:04.457792
...
```

## Run the Subscriber

In a separate terminal window, create a subscriber and start consuming events.

```bash
$ python subscriber.py
```

You'll know it's working when your terminal is filled with events such as:

```bash
New steam report received: {'game': 'The Murder Hotel Demo', 'id': 2484850, 'count': 42}
New steam report received: {'game': 'Fantasy Grounds - FG Grasslands Map Pack', 'id': 2484870, 'count': 1}
New steam report received: {'game': 'Phantom Peak', 'id': 2484240, 'count': 42}
New steam report received: {'game': 'Jolly Putt - Mini Golf & Arcade', 'id': 2484340, 'count': 42}
New steam report received: {'game': 'Fat Rat Pinball', 'id': 2484420, 'count': 42}
...
```