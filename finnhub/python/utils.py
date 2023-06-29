from datetime import datetime


async def handle_ack(ack):
    ts = datetime.fromtimestamp(ack.committed.seconds + ack.committed.nanos / 1e9)
    print(f"Event committed at {ts}")

async def handle_nack(nack):
    print(f"Could not commit event {nack.id} with error {nack.code}: {nack.error}")