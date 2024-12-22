import logging
import random
import asyncio
import string
from dataclasses import dataclass
from config import config
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level = logging.INFO)

@dataclass
class Message:
    """dataclass representing an SMS message"""
    id: str
    content: str

class ProducerModel:
    """
    Generates a configurable amount of SMS messages of up to length 100.

    Attributes:
        queue (asyncio.Queue): The queue to handle generated messages.
        messages_produced (int): Count of how many messages were produced.
        running (boolean): Status of producer function.
    """

    def __init__(self):
        self.queue = asyncio.Queue()
        self.messages_produced = 0
        self.running = False
        logger.info("Initialized Producer with an empty queue")

    def generate_message(self) -> Message:
        """
        Generate a random message of length 1-100 and updates total messages added to queue

        Returns: 
            Message: newly created Message object
        """
        msg_length = random.randint(1,100)
        characters = string.ascii_letters + string.digits + ' '
        random_msg = ''.join(random.choices(characters, k = msg_length))

        message = Message(
            id = f"MSG_{int(datetime.now().timestamp())}_{self.messages_produced}",
            content = random_msg
        )
        self.messages_produced +=1
        return message

    async def produce_messages(self):
        """
        Calls generator function and adds messages to queue asynchronously
        """
        try:
            self.running = True
            logger.info("Starting production of messages")
            while(self.messages_produced < config.total_messages and self.running):
                message = self.generate_message()
                await self.queue.put(message) #asynchronous operation of adding messages to queue
            await self.add_sentinel_vals()
            logger.info("Message production completed")


        except Exception as e:
            logger.error(f"Failed message production: {e}")
            self.running = False
            raise 

    async def add_sentinel_vals(self):
        """
        Adds sentinel values to queue to tell consumers to stop processing
        """
        for _ in range(config.num_senders):
            await self.queue.put(None)
        logger.info("Added sentinel values to queue")