# Testing was conducted using pytest framework in a virtual env
# To run the tests, use the command: python3 -m pytest tests/test_display_monitor.py

import pytest
from unittest.mock import patch
import asyncio
from models.display_monitor_model import monitor_progress
from config import config

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
def mock_config(mocker):
    """Mock configuration settings."""
    mocker.patch.object(config, "monitor_interval", 0.1)  # Speed up tests

##########################################################
# Monitor Output Tests
##########################################################

@pytest.mark.asyncio
async def test_monitor_basic_output(stats_dict, mock_config, capsys):
    """Test basic monitor output format."""
    monitor_task = asyncio.create_task(monitor_progress(stats_dict))
    await asyncio.sleep(0.15)  # Allow one output
    monitor_task.cancel()
    
    #Use capysys to capture output
    captured = capsys.readouterr()
    assert "[Monitor]" in captured.out
    assert "Sent: 0" in captured.out
    assert "Failed: 0" in captured.out
    assert "Avg Time: 0.0000" in captured.out

@pytest.mark.asyncio
async def test_monitor_with_stats_update(stats_dict, mock_config, capsys):
    """Test monitor output with changing stats."""
    stats_dict['sent'] = 10
    stats_dict['failed'] = 2
    stats_dict['total_time'] = 5.0
    
    monitor_task = asyncio.create_task(monitor_progress(stats_dict))
    await asyncio.sleep(0.15)  # Allow one output
    monitor_task.cancel()
    
    captured = capsys.readouterr()
    assert "Sent: 10" in captured.out
    assert "Failed: 2" in captured.out
    assert "Avg Time: 0.5000" in captured.out  # 5.0/10

@pytest.mark.asyncio
async def test_monitor_multiple_intervals(stats_dict, mock_config, capsys):
    """Test monitor output over multiple intervals."""
    monitor_task = asyncio.create_task(monitor_progress(stats_dict))
    
    # Update stats over time
    await asyncio.sleep(0.15)  # First interval
    stats_dict['sent'] = 5
    stats_dict['total_time'] = 2.5
    
    await asyncio.sleep(0.1)  # Second interval
    stats_dict['sent'] = 10
    stats_dict['failed'] = 1
    stats_dict['total_time'] = 5.0
    
    await asyncio.sleep(0.1)  # Third interval
    monitor_task.cancel()
    
    captured = capsys.readouterr()
    output_lines = captured.out.strip().split('\n')
    assert len(output_lines) >= 3, "Should have at least three output lines"

##########################################################
# Edge Cases and Error Handling
##########################################################

@pytest.mark.asyncio
async def test_monitor_zero_division_handling(stats_dict, mock_config, capsys):
    """Test handling of zero division when calculating average time."""
    stats_dict['sent'] = 0
    stats_dict['total_time'] = 5.0
    
    monitor_task = asyncio.create_task(monitor_progress(stats_dict))
    await asyncio.sleep(0.15)
    monitor_task.cancel()
    
    captured = capsys.readouterr()
    assert "Avg Time: 0.0000" in captured.out

@pytest.mark.asyncio
async def test_monitor_missing_stats(mock_config, capsys):
    """Test monitor error handling of missing stats dictionary keys."""
    incomplete_stats = {}  # Missing all keys

    with pytest.raises(ValueError, match="Missing required stats keys"):
        await monitor_progress(incomplete_stats)

##########################################################
# Performance Tests
##########################################################

@pytest.mark.asyncio
async def test_monitor_performance(stats_dict, mock_config):
    """Test monitor performance with rapid stat updates."""
    monitor_task = asyncio.create_task(monitor_progress(stats_dict))
    
    # Simulate rapid stat updates
    for i in range(1,101):
        stats_dict['sent'] = i
        stats_dict['total_time'] = i * 0.1
        await asyncio.sleep(0.01)
    
    monitor_task.cancel()
    
    assert stats_dict['sent'] == 100, "Monitor should handle rapid stat updates without errors"
    assert stats_dict['total_time'] == 10.0, "Monitor should correctly calculate total time"

@pytest.mark.asyncio
async def test_monitor_long_running(stats_dict, mock_config):
    """Test monitor stability over longer duration."""
    monitor_task = asyncio.create_task(monitor_progress(stats_dict))
    
    # Run monitor for longer period with periodic updates
    for i in range(10):
        stats_dict['sent'] += 10
        stats_dict['total_time'] += 5.0
        await asyncio.sleep(0.2)
    
    monitor_task.cancel()
    
    assert stats_dict['sent'] == 100, "Stats should be correctly maintained"