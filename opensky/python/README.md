# OpenSky Python

Connect to the OpenSky API from Python to get access to real-time flight position and velocity data around the world!

## Setup

This implementation relies on the `python-opensky` package and the `pyensign` package.

```
$ pip install -r requirements.txt
```

Note: `python-opensky` is a wrapper around the official [OpenSky Python API](https://openskynetwork.github.io/opensky-api/python.html) that allows us to interact with OpenSky from async code.

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
publisher = FlightsPublisher(ensign_creds=<path-to-ensign-creds>, opensky_creds=<path-to-opensky-creds-json-file>)
publisher.run()
```

You should see some acks come back, indicating that events are being committed by Ensign.

```
Event committed at 2023-06-27 13:18:55.810252
Event committed at 2023-06-27 13:18:55.810257
Event committed at 2023-06-27 13:18:55.812141
```

### Publisher Configuration

Specify the latitudes and longitudes of the area you want to record flights over.

```python
FlightsPublisher(
    # Roughly, record flights over the continental United States
    min_latitude=-66,
    max_latitude=49,
    min_longitude=-124,
    max_longitude=24
)
```

Specify the interval in seconds to wait in between polling the OpenSky API.

```python
FlightsPublisher(
    interval=5*60 # Get flight vectors every 5 minutes
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
subscriber = FlightsSubscriber(ensign_creds=<path-to-ensign-creds-json-file>)
subscriber.run()
```

You should see the data come in periodically.

```
Received flight vector: {'icao24': 'a11d08', 'callsign': 'N171BL  ', 'origin_country': 'United States', 'time_position': 1687890269, 'last_contact': 1687890269, 'longitude': -77.8813, 'latitude': 35.8695, 'geo_altitude': 68.58, 'on_ground': False, 'velocity': 44.38, 'true_track': 214.61, 'vertical_rate': -3.9, 'sensors': None, 'barometric_altitude': 160.02, 'transponder_code': None, 'special_purpose_indicator': False, 'position_source': 0, 'category': 0}

Received flight vector: {'icao24': '4b1902', 'callsign': 'SWR86   ', 'origin_country': 'Switzerland', 'time_position': 1687890269, 'last_contact': 1687890269, 'longitude': -62.009, 'latitude': 48.1098, 'geo_altitude': 11468.1, 'on_ground': False, 'velocity': 224.51, 'true_track': 251.98, 'vertical_rate': 0.0, 'sensors': None, 'barometric_altitude': 10972.8, 'transponder_code': None, 'special_purpose_indicator': False, 'position_source': 0, 'category': 1}

Received flight vector: {'icao24': 'e94c88', 'callsign': 'BOV709  ', 'origin_country': 'Bolivia', 'time_position': 1687890270, 'last_contact': 1687890270, 'longitude': -58.5902, 'latitude': -34.7019, 'geo_altitude': 5905.5, 'on_ground': False, 'velocity': 175.39, 'true_track': 337.95, 'vertical_rate': 12.03, 'sensors': None, 'barometric_altitude': 5775.96, 'transponder_code': '0330', 'special_purpose_indicator': False, 'position_source': 0, 'category': 0}
```