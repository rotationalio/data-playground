# OpenSky Python Publisher and Subscriber

This is a Python implementation that publishes flight position data to an Ensign topic and subscribes to that topic.

## Setup

This implementation relies on the `python-opensky` package and the `pyensign` package.

```
$ pip install -r requirements.txt
```

## Publish Flight Data

Create an [Ensign API key](https://rotational.app) with the permissions:

```
publisher
topics:create
topics:read
```

Save your Ensign API key credentials to a JSON file.

Alternatively, specify Ensign credentials in the environment.
```
$ export ENSIGN_CLIENT_ID=<your-client-id>
$ export ENSIGN_CLIENT_SECRET=<your-client-secret>
```

Create an [OpenSky account](https://opensky-network.org/) and API key. Create a JSON file with your account credentials:

```json
{
    "username": <your-opensky-username>,
    "password": <your-opensky-password>
}
```

Create a publisher and start publishing events.

```python
publisher = FlightsPublisher(ensign_creds=<path-to-ensign-creds>, opensky_creds=<path-to-opensky-creds>)
publisher.run()
```



### Publisher Configuration

Specify the latitudes and longitudes of the area you want to record flights from.

```python
FlightsPublisher(
    min_latitude=-66,
    max_latitude=49,
    min_longitude=-124,
    max_longitude=24
)
```

Specify the interval in seconds to wait in between polling the OpenSky API.

```python
FlightsPublisher(
    interval=5*60
)
```

## Subscribe to Flight Events

Create an [Ensign API key](https://rotational.app) with the permissions:

```json
subscriber
topics:read
```

Save your Ensign API key credentials to a JSON file.

Alternatively, specify Ensign credentials in the environment.
```
$ export ENSIGN_CLIENT_ID=<your-client-id>
$ export ENSIGN_CLIENT_SECRET=<your-client-secret>
```

Create a subscriber and start consuming events.

```python
subscriber = FlightsSubscriber(ensign_creds=<path-to-ensign-creds>)
subscriber.run()
```