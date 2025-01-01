import logging
import random
import asyncio
import time
from .producer_model import Message
from config import config
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level = logging.INFO)

class SenderModel:
    """
    Creates a sender that can asynchronously process and send messages from the producer queue.

    Attributes:
        id (int): unique ID of sender.
        running (boolean): status of sender.
        queue (aysncio.Queue): message queue to be processed.
        stats (dict): Information about message success, failure, and time.
        failure_rate (float): Chance of sender failing to send a message.
        mean_time (float): Average time it takes for sender to send message in an exp. distirbution.
    """

    def __init__(self, id: int, queue: asyncio.Queue, stats: dict, failure_rate: float = config.sender_failure, mean_time: float = config.sender_mean_time):
        self.id = id
        self.running = False
        self.queue = queue
        self.stats = stats
        self.failure_rate = failure_rate
        self.mean_time = mean_time
        logger.info(f"Initialized sender with SenderID:{id}")
    
    async def send_message(self, message: Message):
        """
        Simulate sending a single message with configurable delay and failure rate.
        
        Args:
            message (Message): The message to send.
        """
        start_time = time.perf_counter()

        try:
            delay = random.expovariate(1.0/self.mean_time) #exponential distribution 
            await asyncio.sleep(delay) #simulate message delay

            if random.random() < self.failure_rate: #simulate failure
                self.stats['failed'] += 1
                logger.warning(f"Sender {self.id}: failed to send message")
            else:
                self.stats['sent'] +=1
                elapsed_time = time.perf_counter() - start_time
                self.stats['total_time'] += elapsed_time
                logger.info(f"Sender {self.id}: sent message = {message.content} successfully")
                print(f"Sender {self.id}: sent message = {message.content} successfully")

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self.stats['failed'] +=1
            raise

    async def run(self):
        """
        Main loop that continuously processes messages from the queue asynchronously.
        Stops when a sentinel value of None is received.
        """
        self.running = True
        logger.info(f"Sender {self.id}: starting message processing")

        try:
            while self.running:
                message = await self.queue.get()
                if message is None:  # Sentinel value received
                    logger.info(f"Sender {self.id}: recieved sentinel")
                    self.queue.task_done()
                    break
                await self.send_message(message)
                self.queue.task_done()

        
        except Exception as e:
            logger.error(f"Error in loop: {e}")
            self.running = False
            raise


        finally:
            self.running = False

    




        

    
