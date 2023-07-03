# Steam Python

Connect to the Steam API to get access to a list of steam games and they're current player count.

## Setup

Code for the Pyensign steam example will use the `pyensign` package to create a publisher that will collect data from the Steam API and a subscriber that will collect the data.  

Install requirements

```
$ pip install -r requirements.txt
```

## Publish Steam Game Data

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

Get a [free Steam API key](https://cran.r-project.org/web/packages/CSGo/vignettes/auth.html) from Steam. Specify this API key in the environment.

```
$ export STEAM_API_KEY=<your-steam-api-key>
```

Create a publisher and start publishing events.

```python
publisher = SteamPublisher()
publisher.run()
```

You should see some acks come back, indicating that events are being committed by Ensign.

```
Event committed at 2023-06-27 13:18:55.810252
Event committed at 2023-06-27 13:18:55.810257
Event committed at 2023-06-27 13:18:55.812141
```

Create a subscriber and start consuming events.

```python
subscriber = SteamSubscriber()
subscriber.run()
```
