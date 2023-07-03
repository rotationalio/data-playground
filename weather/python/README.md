# Weather

Connect directly to the NOAA weather API to get forecasts for locations around the US!

## Getting Started

Ready to turn on the weather firehose? Let's do it!

### Install the Dependencies

```bash
git clone git@github.com:rotationalio/data-playground.git
cd data-playground/weather/python
pip install -r requirements.txt
```

### API Keys
The NOAA API doesn't currently require API keys (though they may cut you off if you
ping them too frequently).

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

### Locations
The publisher has a hardcoded list of locations to check the weather in (check the top of the file called `publisher.py`). You can change to locations of interest to you!

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
Event committed at 2023-06-26 19:18:16.708653
Event committed at 2023-06-26 19:18:16.708698
Event committed at 2023-06-26 19:18:16.713985
Event committed at 2023-06-26 19:18:16.714014
...
```

And in your subscriber terminal, you'll see the data:

```bash
yrcomputersnickname:weather YOURNAMEHERE$ python subscriber.py
New weather report received: {'name': 'This Afternoon', 'summary': 'Mostly Cloudy', 'temperature': 71, 'units': 'F', 'daytime': True, 'start': '2023-06-26T14:00:00-08:00', 'end': '2023-06-26T18:00:00-08:00'}
New weather report received: {'name': 'Tonight', 'summary': 'Mostly Cloudy then Isolated Rain Showers', 'temperature': 51, 'units': 'F', 'daytime': False, 'start': '2023-06-26T18:00:00-08:00', 'end': '2023-06-27T06:00:00-08:00'}
New weather report received: {'name': 'Tuesday', 'summary': 'Isolated Rain Showers', 'temperature': 73, 'units': 'F', 'daytime': True, 'start': '2023-06-27T06:00:00-08:00', 'end': '2023-06-27T18:00:00-08:00'}
New weather report received: {'name': 'Tuesday Night', 'summary': 'Mostly Cloudy', 'temperature': 52, 'units': 'F', 'daytime': False, 'start': '2023-06-27T18:00:00-08:00', 'end': '2023-06-28T06:00:00-08:00'}
...
```