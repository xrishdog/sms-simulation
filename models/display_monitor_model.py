# The formatting of display outputs was assisted by Claude 3.5

import asyncio
from config import config
import time

def validate_stats(stats: dict):
    """
    Check to ensure that stats dictionary has the required keys for stats monitoring

    Attributes:
        stats (dict): A dictionary of relevant stats to be displayed
    """
    required_keys = {'sent', 'failed', 'total_time'}
    missing_keys = required_keys - stats.keys()
    if missing_keys:
        raise ValueError("Missing required stats keys")

async def monitor_progress(stats: dict):
    """
    Logs stats collected through senders in console

    Attributes:
        stats (dict): A dictionary of relevant stats to be displayed
    """
    validate_stats(stats)
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

