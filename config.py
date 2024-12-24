from dataclasses import dataclass 

@dataclass
class Config:
    total_messages: int = 1000
    message_length: int = 100
    num_senders: int = 50
    monitor_interval: float = 5.0 # in seconds
    sender_failure: float = 0.15 # 15%
    sender_mean_time: float = 2.0 # in seconds

config = Config()