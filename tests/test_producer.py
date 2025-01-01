# Testing was conducted using pytest framework in a virtual env
# To run the tests, use the command: python3 -m pytest tests/test_producer.py
# Claude 3.5 was used to help generate docstrings and some base test cases

import pytest
from unittest.mock import patch
import asyncio
import string
from models.producer_model import ProducerModel, Message
from config import config

##########################################################
# Fixtures
##########################################################

@pytest.fixture
def producer_model():
    """Fixture to create a ProducerModel for each test."""
    queue = asyncio.Queue()
    return ProducerModel(queue)

@pytest.fixture
def mock_config_five(mocker):
    """Mock configuration settings for five messages"""
    mocker.patch.object(config, "total_messages", 5)
    mocker.patch.object(config, "num_senders", 2)

@pytest.fixture
def mock_config_thousand(mocker):
    """Mock configuration settings for a thousand messages."""
    mocker.patch.object(config, "total_messages", 1000)
    mocker.patch.object(config, "num_senders", 10)

@pytest.fixture
def mock_config_million(mocker):
    """Mock configuration settings for million messages."""
    mocker.patch.object(config, "total_messages", 1000000)
    mocker.patch.object(config, "num_senders", 200)

##########################################################
# Message Generation Tests
##########################################################

def test_generate_message_structure(producer_model):
    """Test if generated message has correct structure and incrementing IDs."""
    message = producer_model.generate_message()
    
    assert isinstance(producer_model.queue, asyncio.Queue), "Should have an asyncio.Queue instance"
    assert isinstance(message, Message), "Should return a Message object"
    assert message.id.startswith("MSG_"), "Message ID should start with MSG_"
    assert 1<= len(message.content) <= 100, "Message content should not exceed 100 characters"
    assert producer_model.messages_produced == 1, "Should increment messages_produced counter"

def test_generate_message_unique_ids(producer_model):
    """Test that generated messages have unique IDs."""
    message1 = producer_model.generate_message()
    message2 = producer_model.generate_message()
    
    assert message1.id != message2.id, "Message IDs should be unique"
    assert producer_model.messages_produced == 2, "Should increment counter for each message"

def test_generate_message_ten(producer_model):
    """Test if generated message content meets constraints."""
    for _ in range(10):  # Test 10 messages
        message = producer_model.generate_message()
        assert 1 <= len(message.content) <= 100, "Content length should be between 1 and 100"
        assert all(c in string.ascii_letters + string.digits + ' ' for c in message.content), \
            "Content should only contain letters, numbers, and spaces"
    assert producer_model.messages_produced == 10

def test_generate_message_tenthousand(producer_model):
    """Test if generated message content meets constraints."""
    for _ in range(1000):  # Test 1000 messages
        message = producer_model.generate_message()
        assert 1 <= len(message.content) <= 100, "Content length should be between 1 and 100"
        assert all(c in string.ascii_letters + string.digits + ' ' for c in message.content), \
            "Content should only contain letters, numbers, and spaces"
    assert producer_model.messages_produced == 1000

def test_generate_message_million(producer_model):
    """Test if generated message content meets constraints."""
    for _ in range(1000000):  # Test 1000000 messages
        message = producer_model.generate_message()
        assert 1 <= len(message.content) <= 100, "Content length should be between 1 and 100"
        assert all(c in string.ascii_letters + string.digits + ' ' for c in message.content), \
            "Content should only contain letters, numbers, and spaces"
    assert producer_model.messages_produced == 1000000

##########################################################
# Message Production Tests
##########################################################

#following 3 tests are for the produce_messages method for 5, 100 and 1 million messages

@pytest.mark.asyncio
async def test_produce_messages_completion_five(producer_model, mock_config_five):
    """Test if message production completes successfully."""
    await producer_model.produce_messages()
    
    assert producer_model.messages_produced == config.total_messages, \
        "Should produce configured number of messages"
    assert producer_model.queue.qsize() == config.total_messages + config.num_senders, \
        "Queue should contain messages plus sentinel values"
    
@pytest.mark.asyncio
async def test_produce_messages_completion_thousand(producer_model, mock_config_thousand):
    """Test if message production completes successfully."""
    await producer_model.produce_messages()

    assert producer_model.messages_produced == config.total_messages, \
        "Should produce configured number of messages"
    assert producer_model.queue.qsize() == config.total_messages + config.num_senders, \
        "Queue should contain messages plus sentinel values"

@pytest.mark.asyncio
async def test_produce_messages_completion_million(producer_model, mock_config_million):
    """Test if message production completes successfully."""
    await producer_model.produce_messages()
    
    assert producer_model.messages_produced == config.total_messages, \
        "Should produce configured number of messages"
    assert producer_model.queue.qsize() == config.total_messages + config.num_senders, \
        "Queue should contain messages plus sentinel values"

@pytest.mark.asyncio
async def test_produce_messages_sentinel_values(producer_model, mock_config_five):
    """Test if correct number of sentinel values are added."""
    await producer_model.produce_messages()
    
    sentinel_count = 0
    while not producer_model.queue.empty():
        message = await producer_model.queue.get()
        if message is None:
            sentinel_count += 1
    
    assert sentinel_count == config.num_senders, \
        "Should add correct number of sentinel values"

@pytest.mark.asyncio
async def test_produce_messages_error_handling(producer_model):
    """Test error handling during message production."""
    with patch.object(producer_model, 'generate_message', side_effect=Exception("Test error")):
        
        with pytest.raises(Exception, match="Test error"):
            await producer_model.produce_messages()
        
        assert not producer_model.running, "Should set running to False on error"

@pytest.mark.asyncio
async def test_queue_operations(producer_model):
    """Test basic queue operations during message production."""
    config.total_messages = 3  # Small number for testing
    await producer_model.produce_messages()
    
    messages = []
    while not producer_model.queue.empty():
        message = await producer_model.queue.get()
        if message is not None:
            messages.append(message)
    
    assert len(messages) == 3, "Should retrieve expected number of messages"
    assert all(isinstance(m, Message) for m in messages), "All items should be Message objects"

##########################################################
# State Management Tests
##########################################################

def test_initial_state(producer_model):
    """Test initial state of ProducerModel."""
    assert producer_model.messages_produced == 0, "Should start with zero messages"
    assert not producer_model.running, "Should start in non-running state"
    assert isinstance(producer_model.queue, asyncio.Queue), "Should have a Queue instance"

@pytest.mark.asyncio
async def test_zero_messages_config(producer_model, mock_config_thousand):
    """Test behavior when producing zero messages."""
    config.total_messages = 0
    await producer_model.produce_messages()
    
    assert producer_model.messages_produced == 0, "Should not produce any messages"
    assert producer_model.queue.qsize() == config.num_senders, \
        "Should only contain sentinel values"

@pytest.mark.asyncio
async def test_running_state_management(producer_model, mock_config_million):
    """Test proper management of running state."""
    assert not producer_model.running, "Should start as not running"
    #assert config.total_messages == 5, "Should be configured for 5 messages"
    
    production_task = asyncio.create_task(producer_model.produce_messages())
    await asyncio.sleep(0.1)
    assert producer_model.running

    await production_task
    assert not producer_model.running, "Should not be running after completion"

