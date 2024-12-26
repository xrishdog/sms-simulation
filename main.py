import asyncio
import time
from models.producer_model import ProducerModel
from models.sender_model import SenderModel
from models.display_monitor_model import monitor_progress
from config import config

async def main():
    start_time = time.time()
    queue = asyncio.Queue() # main datastructure to handle messages

    stats = {
        'sent': 0,
        'failed': 0,
        'total_time': 0.0
    }

    #initialize producer (s)
    producer = ProducerModel(queue) 
    producer_task = asyncio.create_task(producer.produce_messages())

    sender_tasks = []
    #initialize senders
    for i in range(config.num_senders):
        sender = SenderModel(i, queue, stats)
        new_task = asyncio.create_task(sender.run())
        sender_tasks.append(new_task)

    #initialize monitor
    monitor_task = asyncio.create_task(monitor_progress(stats))

    #==============================Start Async Tasks==============================

    await producer_task
    await queue.join() #wait for senders to finish process all messages in queue
    for task in sender_tasks: #extra check to make sure that tasks have also finished
        await task 

    monitor_task.cancel() #clean up resources
    try:
        await monitor_task
    except asyncio.CancelledError:
        pass
    
    #coudl display final stats
    elapsed_time = time.time() - start_time
    sent = stats.get('sent', 0)
    failed = stats.get('failed', 0)
    total_time = stats.get('total_time', 0.0)
    avg_time = (total_time / sent) if sent > 0 else 0.0
    print(f"[Monitor] {elapsed_time}s, Sent: {sent}, Failed: {failed}, Avg Time: {avg_time:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(main())


