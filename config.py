from dataclasses import dataclass 
@dataclass
class Config:
    total_messages: int = 1000
    message_length: int = 100
    num_senders: int = 5
    monitor_interval: float = 5.0 # in seconds

config = Config()