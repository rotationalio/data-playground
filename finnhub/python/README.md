# FinnHub Python

Connect to the Finnhub API to get access to real-time stock market data and play around with generating your own trading and investment strategies!

## Setup

FinnHub requires the `websockets` package for connecting to its API and the example code will use the `pyensign` package to create a publisher that will collect data from FinnHub and a subscriber that will run a model pipeline using the `river` package to generate predictions.  

Create a virtual environment

```
$ virtualenv venv
```

Activate the virtual environment

```
$ source venv/bin/activate
```

Install requirements

```
$ pip install -r requirements.txt
```

## Publish Stock Market Data

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

Get a [free API key](https://finnhub.io/dashboard) from FinnHub. Specify this API key in the environment.

```
$ export FINNHUB_API_KEY=<your-finnhub-api-key>
```

Create a publisher and start publishing events.

```python
publisher = TradesPublisher()
publisher.run()
```

You should see some acks come back, indicating that events are being committed by Ensign.

```
Event committed at 2023-06-27 13:18:55.810252
Event committed at 2023-06-27 13:18:55.810257
Event committed at 2023-06-27 13:18:55.812141
```

### Publisher Configuration

By default, the publisher publishes trades for AAPL, AMZN, and MSFT.  You can specify your own custom list as follows:

```python
TradesPublisher(symbols=[<your-custom-symbols>])
```

## Subscribe to Trade Events and Publish predictions to a new topic

Create an [Ensign API key](https://rotational.app) with the permissions:

```
subscriber
topics:create
topics:read
```

Note that since this subscriber will also publish to a new topic (which is not necessary if the subscriber is only consuming messages), it will require the `topics:create` permission.

Alternatively, specify Ensign credentials in the environment.
```
$ export ENSIGN_CLIENT_ID=<your-client-id>
$ export ENSIGN_CLIENT_SECRET=<your-client-secret>
```

Or you can create config.py file within your python folder and provide Ensign credentials as follows:
'''
CLIENT_ID = <your-client-id>
CLIENT_SECRET = <your-client-secret> 
FINNHUB_API_KEY = <your-finnhub_api_key>
'''

Create a subscriber and start consuming events.

```python
subscriber = TradesSubscriber()
subscriber.run()
```

The subscriber takes the events and runs a model pipeline that generates trade predictions and publishes the predictions to a new `predictions` topic. You will periodically see messages being printed to the screen that display the symbol, timestamp, price, and the predicted price.

```json
{'symbol': 'AMZN', 'time': '12:18:03', 'price': '127.88', 'price_pred': '183.5796'}
{'symbol': 'AAPL', 'time': '12:18:03', 'price': '189.36', 'price_pred': '181.8145'}
{'symbol': 'MSFT', 'time': '12:18:03', 'price': '334.71', 'price_pred': '180.2801'}
```

You should also see some acks come back (since the subscriber is also publishing events), indicating that events are being committed by Ensign.

```
Event committed at 2023-06-27 13:18:55.810252
Event committed at 2023-06-27 13:18:55.810257
Event committed at 2023-06-27 13:18:55.812141
```