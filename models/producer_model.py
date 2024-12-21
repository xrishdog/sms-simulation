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
    Generates a configurable amount of SMS messages of up to length 100

    Attributes:
        queue (asyncio.Queue): The queue to place generated messages
        total_messages (int): Total number of messages to produce
    """

    def __init__(self):
        self.queue = asyncio.Queue()
        self.messages_produced = 0
        self.running = False
        logger.info("Initialized Producer with an empty queue")

    def generate_message(self) -> Message:
        """
        Generate a random message of length 1-100 and update total messages

        Returns: 
            Message: newly created Message object
        """
        #define message to have at least one character
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
        Docstring here
        """
        try:
            self.running = True
            logger.info("Starting production of messages")
            while(self.messages_produced < config.total_messages and self.running):
                message = self.generate_message()
                #asynchronous operation of adding messages to queue
                await self.queue.put(message)
            
            logger.info("Message production completed")
        except Exception as e:
            logger.info(f"Failed message production: {e}")
            self.running = False
            raise 

       #may need to handle sentinel value here