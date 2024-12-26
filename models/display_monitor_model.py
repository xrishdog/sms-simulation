# The formatting of display outputs was assisted by Claude 3.5

import asyncio
from config import config
import time

async def monitor_progress(stats: dict):
    """
    Logs stats collected through senders in console

    Attributes:
        stats (dict): A dictionary of relevant stats to be displayed
    """
    counter = 0

    while True:
        await asyncio.sleep(config.monitor_interval)
        counter +=1
        current_time = counter * config.monitor_interval #keep track of time elapsed

        sent = stats.get('sent', 0)
        failed = stats.get('failed', 0)
        total_time = stats.get('total_time', 0.0)
        avg_time = (total_time / sent) if sent > 0 else 0.0
        print(f"[Monitor] {current_time}s, Sent: {sent}, Failed: {failed}, Avg Time: {avg_time:.4f} seconds")