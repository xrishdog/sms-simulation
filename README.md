# SMS Simulation

An asynchronous message queing system that simulates SMS message generation and sending. Built with Python's asyncio framework.
The goal of this simulation is to demonstrate how message generation and send requests are handled in an efficient manner.
The asynchronous producer-consumer model is used to distribute messages and balance load among different senders.
Documentation can be viewed in ```docs/technical_documentation.pdf```

## System Requirements

- Python 3.9+
- pytest for running tests


## Configuration

Edit `config.py` to customize system behavior.
Default configuration:

```python
total_messages: int = 1000    # Total messages to process
message_length: int = 100     # Maximum message length
num_senders: int = 50        # Number of concurrent senders
monitor_interval: float = 5.0 # Statistics display interval
sender_failure: float = 0.15  # Message failure rate
sender_mean_time: float = 2.0 # Average processing time
```

## Usage

Run the simulation:
```bash
python main.py
```

### Sample Output
```
[Monitor] 5.0s, Sent: 127, Failed: 23, Avg Time: 1.8754 seconds
[Monitor] 10.0s, Sent: 256, Failed: 44, Avg Time: 1.9123 seconds
[Final] 15.234s, Sent: 850, Failed: 150, Avg Time: 1.8932 seconds
```

## Project Structure


```
sms-simulation/
├── models/
│   ├── producer_model.py     # Message generation
│   ├── sender_model.py       # Message processing
│   └── display_monitor_model.py  # Statistics monitoring
├── tests/
│   ├── test_producer.py
│   ├── test_sender.py
│   └── test_display_monitor.py
├── docs/
│   └── technical_documentation.pdf
├── config.py                 # System configuration
├── main.py                   # Entry point
└── README.md
```

## Testing

Run all tests:
```bash
python3 -m pytest tests/
```

Run specific test files:
```bash
python3 -m pytest tests/test_sender.py
python3 -m pytest tests/test_producer.py
python3 -m pytest tests/test_display_monitor.py
```

### Test Categories
- Basic functionality tests
- Concurrent operation tests
- Performance tests
- Error handling tests
- Edge case tests


## Implementation Details

- **ProducerModel**: Generates random messages with configurable length.
- **SenderModel**: Processes messages with configurable network delays and failure rates.
The number of producers and consumers can also be configured.
- **Queue**: Central asyncio.Queue for message passing. This is centralized among models.
- **DisplayMonitorModel**: Real-time performance statistics which can be configured to output every n seconds.
- **Config**: Centralized system parameters


## Author

Krish Asija (@xrishdog)

