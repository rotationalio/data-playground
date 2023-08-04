import json
import asyncio
from datetime import datetime

from pyensign.events import Event
from pyensign.ensign import Ensign
from river import compose
from river import linear_model
from river import preprocessing

from utils import handle_ack, handle_nack


class TradesSubscriber:
    """
    TradesSubscriber subscribes to trading events from Ensign and runs an
    online model pipeline and publishes predictions to a new topic.
    """

    def __init__(self, sub_topic="trades", pub_topic="predictions",ensign_cred=''):
        self.sub_topic = sub_topic
        self.pub_topic = pub_topic
        self.ensign = Ensign(
                             cred_path=ensign_cred
                             )
        self.model = self.build_model()
    
    def run(self):
        """
        Run the subscriber forever.
        """
        asyncio.run(self.subscribe())

    def build_model(self):
        model = compose.Pipeline(
            ('scale', preprocessing.StandardScaler()),
            ('lin_reg', linear_model.LinearRegression())
        )
        return model
    
    def get_timestamp(self, epoch):
        """
        converts unix epoch to datetime
        """
        epoch_time = epoch / 1000.0
        timestamp = datetime.fromtimestamp(epoch_time)
        return timestamp
    
    async def run_model_pipeline(self, event):
        """
        Train an online model and publish predictions to a new topic.
        Run your super smart model pipeline here!
        """
        data = json.loads(event.data)
        # convert unix epoch to datetime
        timestamp = self.get_timestamp(data["timestamp"])
        # extract the microsecond component and use it as a model feature
        x = {"microsecond" : timestamp.microsecond}
        # generate a prediction
        price_pred = round(self.model.predict_one(x), 4)
        price = data["price"]
        # pass the actual trade price to the model
        self.model.learn_one(x, price)

        # create a message that contains the predicted price and the actual price
        message = dict()
        message["symbol"] = data["symbol"]
        message["time"] = timestamp.strftime("%H:%M:%S")
        message["price"] = str(data["price"])
        message["price_pred"] = str(price_pred)
        print(message)


        # create an Ensign event and publish to the predictions topic
        event = Event(json.dumps(message).encode("utf-8"), mimetype="application/json")
        # Get the topic ID from the topic name.
        topic_id = await self.ensign.topic_id(self.pub_topic)
        await self.ensign.publish(topic_id, event, on_ack=handle_ack, on_nack=handle_nack)


    async def subscribe(self):
        """
        Subscribe to trading events from Ensign and run an
        online model pipeline and publish predictions to a new topic.
        """

        # Get the topic ID from the topic name.
        topic_id = await self.ensign.topic_id(self.sub_topic)

        # Subscribe to the topic.
        # self.run_model_pipeline is a callback function that gets executed when 
        # a new event arrives in the topic
        async for event in self.ensign.subscribe(topic_id):
             await self.run_model_pipeline(event)

if __name__ == "__main__":
    subscriber = TradesSubscriber(ensign_cred='secret/ensign_cred.json')
    subscriber.run()