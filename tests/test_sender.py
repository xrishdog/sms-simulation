# Testing was conducted using pytest framework in a virtual env
# To run the tests, use the command: python3 -m pytest tests/test_sender.py

import pytest
from unittest.mock import patch
import asyncio
import time
from models.sender_model import SenderModel, Message
from models.producer_model import ProducerModel
from config import config

import logging
logger = logging.getLogger(__name__)

##########################################################
# Fixtures
##########################################################

@pytest.fixture
def stats_dict():
    """Fixture to create a fresh stats dictionary for each test."""
    return {
        'sent': 0,
        'failed': 0,
        'total_time': 0.0
    }

@pytest.fixture
def shared_queue():
    """Fixture to create a shared queue for testing."""
    return asyncio.Queue()

@pytest.fixture
def sender_model(shared_queue, stats_dict):
    """Fixture to create a SenderModel instance for each test."""
    return SenderModel(1, shared_queue, stats_dict)

@pytest.fixture
def producer_model(shared_queue):
    """Fixture to create a ProducerModel instance for testing."""
    return ProducerModel(shared_queue)

@pytest.fixture
def create_sender(stats_dict, shared_queue):
    """Fixture to create multiple senders with the same queue and stats."""
    def _create_sender(sender_id, sender_failure, sender_mean_time):
        return SenderModel(sender_id, shared_queue, stats_dict, sender_failure, sender_mean_time)
    return _create_sender

# @pytest.fixture
# def create_senders(num_senders, shared_queue, stats_dict):
#     """Mock multiple senders with shared queue."""
#     senders = []
#     for i in range(num_senders):
#         sender = SenderModel(i, shared_queue, stats_dict)
#         senders.append(sender)
#     return senders

@pytest.fixture
def test_message():
    """Fixture to create a test message."""
    return Message(id="TEST_MSG_1", content="This is a test message")

@pytest.fixture
def mock_config(mocker):
    """Mock configuration settings."""
    mocker.patch.object(config, "sender_failure", 0.15)
    mocker.patch.object(config, "sender_mean_time", 2.0)

@pytest.fixture
def mock_config2(mocker):
    """Mock configuration settings."""
    mocker.patch.object(config, "sender_failure", 0.15)
    mocker.patch.object(config, "sender_mean_time", 0.1)

##########################################################
# Message Sending Tests
##########################################################

@pytest.mark.asyncio
async def test_send_message_success(sender_model, test_message, mocker):
    """Test successful message sending."""
    sender_model.failure_rate = 0
    mocker.patch('random.expovariate', return_value=0.1)
    await sender_model.send_message(test_message)
    assert sender_model.stats['sent'] == 1, "Should increment sent counter"
    assert sender_model.stats['failed'] == 0, "Should not increment failed counter"
    assert sender_model.stats['total_time'] > 0, "Should record sending time"

@pytest.mark.asyncio
async def test_send_message_failure(sender_model, test_message, mocker):
    """Test message sending failure."""
    sender_model.failure_rate = 1
    mocker.patch('random.expovariate', return_value=0.1)
    await sender_model.send_message(test_message)
    assert sender_model.stats['sent'] == 0, "Should not increment sent counter"
    assert sender_model.stats['failed'] == 1, "Should increment failed counter"

@pytest.mark.asyncio
async def test_send_message_exception(sender_model, test_message, mocker):
    """Test error handling during message sending."""
    mocker.patch('random.expovariate', side_effect=Exception("Test error"))
    with pytest.raises(Exception, match="Test error"):
        await sender_model.send_message(test_message)
    assert sender_model.stats['failed'] == 1, "Should increment failed counter on exception"

##########################################################
# Run Loop Tests
##########################################################

@pytest.mark.asyncio
async def test_run_loop_basic(sender_model, test_message):
    """Test basic run loop functionality."""
    await sender_model.queue.put(test_message)
    await sender_model.queue.put(None)  # Sentinel value
    await sender_model.run()
    
    assert not sender_model.running, "Should stop running after sentinel"
    assert sender_model.queue.empty(), "Should process all messages"

@pytest.mark.asyncio
async def test_run_loop_multiple_messages(sender_model):
    """Test processing multiple messages in run loop."""
    messages = [
        Message(id=f"TEST_MSG_{i}", content=f"Test content: {i}")
        for i in range(5)
    ]
    for msg in messages:
        await sender_model.queue.put(msg)
    await sender_model.queue.put(None)
    await sender_model.run()

    assert sender_model.queue.empty(), "Should empty the queue"

@pytest.mark.asyncio
async def test_run_loop_error_handling(sender_model, test_message, mocker):
    """Test error handling in run loop."""
    mocker.patch.object(sender_model, 'send_message', side_effect=Exception("Test error")) 
    await sender_model.queue.put(test_message)
    await sender_model.queue.put(None)
    
    with pytest.raises(Exception, match="Test error"):
        await sender_model.run()
    
    assert not sender_model.running, "Should stop running on error"

##########################################################
# Multi-Sender Tests
##########################################################
#These tests use producer model to populate the queue with messages

@pytest.mark.asyncio
async def test_multiple_senders_shared_queue(create_sender, producer_model, shared_queue, mock_config2):
    """Test multiple senders processing messages from a shared queue."""
    config.num_senders = 100
    config.total_messages = 100
    
    # Create and populate queue
    producer_task = asyncio.create_task(producer_model.produce_messages())
    # Create and run multiple senders
    senders = [create_sender(i, config.sender_failure, config.sender_mean_time) for i in range(config.num_senders)]
    sender_tasks = [asyncio.create_task(sender.run()) for sender in senders]
    await producer_task
    await shared_queue.join() #wait for senders to finish process all messages in queue
    for task in sender_tasks: #extra check to make sure that tasks have also finished
        await task 
    
    # Verify results
    stats = senders[0].stats  # All senders share the same stats dict
    total_processed = stats['sent'] + stats['failed']
    assert len(senders) == config.num_senders
    assert total_processed == config.total_messages, "All messages should be processed"
    assert shared_queue.empty(), "Queue should be empty"

@pytest.mark.asyncio
async def test_sender_load_balancing(create_sender, producer_model, shared_queue, mock_config):
    """Test load distribution across multiple senders using producer."""
    config.total_messages = 10000
    config.num_senders = 100
    config.sender_failure = 0.0
    config.sender_mean_time = 0.01  # Speed up test

    
    # Create senders with tracking
    sender_processed = {i: 0 for i in range(config.num_senders)}
    senders = []
    # Modify send_message to track processed messages
    for i in range(config.num_senders):
        sender = create_sender(i, config.sender_failure, config.sender_mean_time)
        original_send = sender.send_message
        
        async def tracked_send(message, sender_id=i, original=original_send):
            await original(message)
            sender_processed[sender_id] += 1
            
        sender.send_message = tracked_send  
        senders.append(sender)
    
    # Run producer and senders
    producer_task = asyncio.create_task(producer_model.produce_messages())
    sender_tasks = [asyncio.create_task(sender.run()) for sender in senders]
    await producer_task
    await shared_queue.join() 
    for task in sender_tasks: 
        await task 
    # Analyze load distribution
    total_processed = sum(sender_processed.values())
    average_per_sender = total_processed / config.num_senders
    max_deviation = max(abs(count - average_per_sender) for count in sender_processed.values())
    
    assert max_deviation <= (average_per_sender* 0.30)  # Allow 30% deviation
    assert total_processed == config.total_messages

@pytest.mark.asyncio
async def test_high_concurrency(create_sender, producer_model, shared_queue, mock_config):
    """Test system under high load with many senders."""
    config.total_messages = 10000
    config.num_senders = 50
    config.sender_mean_time = 0.001
    config.sender_failure = 0.0
    #producer_model.batch_size = 1000

    # Create senders with minimal delay
    senders = [create_sender(i, config.sender_failure, config.sender_mean_time) for i in range(config.num_senders)]
    # Run with timing
    start_time = time.perf_counter()
    producer_task = asyncio.create_task(producer_model.produce_messages())
    sender_tasks = [asyncio.create_task(sender.run()) for sender in senders]
    await producer_task
    await shared_queue.join() 
    for task in sender_tasks: 
        await task 
    end_time = time.perf_counter()

    # Performance verification
    processing_time = end_time - start_time
    messages_per_second = config.total_messages / processing_time
    assert messages_per_second > 10000  # Minimum throughput requirement

@pytest.mark.asyncio
async def test_different_failure_rates(create_sender, producer_model, shared_queue, mock_config):
    """Test system resilience with failing senders."""
    config.total_messages = 100
    config.num_senders = 5
    config.sender_mean_time = 0.01
    
    # Create senders with different failure rates
    senders = []
    for i in range(config.num_senders):
        sender = create_sender(i, i*0.2, config.sender_mean_time)
        senders.append(sender)

    # Run producer and senders
    producer_task = asyncio.create_task(producer_model.produce_messages())
    sender_tasks = [asyncio.create_task(sender.run()) for sender in senders]
    await producer_task
    await shared_queue.join() 
    for task in sender_tasks: 
        await task 

    # Verify all messages were handled
    stats = senders[0].stats
    assert stats['sent'] + stats['failed'] == config.total_messages
    assert shared_queue.empty()

##########################################################
# State Management Tests
##########################################################

@pytest.mark.asyncio
async def test_no_messages(create_sender, producer_model, mock_config, shared_queue):
    """Test behavior when no messages are produced."""
    config.total_messages = 0
    config.num_senders = 3
    producer_task = asyncio.create_task(producer_model.produce_messages())
    senders = [create_sender(i, config.sender_failure, config.sender_mean_time) for i in range(config.num_senders)]
    sender_tasks = [asyncio.create_task(sender.run()) for sender in senders]

    await producer_task
    await shared_queue.join() 
    for task in sender_tasks: 
        await task 
    stats = senders[0].stats
    assert stats['sent'] == 0
    assert stats['failed'] == 0

