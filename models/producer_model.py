import logging
import random
import asyncio
import string
from config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(level = logging.INFO)

class ProducerModel:
    """
    Generates a configurable amount of SMS messages of length 100

    Attributes:
        queue (asyncio.Queue): The queue to place generated messages
        total_messages (int): Total number of messages to produce
    """

    def __init__(self, config: Config):
        self.queue = asyncio.Queue()
        logger.info("Initialized Producer with an empty queue")

    async def generate_messages(self, total_messages):
        for _ in range(total_messages):

            #define message to have at least one character
            msg_length = random.randint(1,100)
            characters = string.ascii_letters + string.digits + ' '
            random_msg = ''.join(random.choices(characters, k = msg_length))
            await self.queue.put(random_msg)

       #may need to handle sentinel value here