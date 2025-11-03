from dataclasses import dataclass

@dataclass
class Config:
    SPACE: str = "         "
    USER_AGENT: str = "Mozilla/5.0 (Linux; Android 8.1.0) AppleWebKit/537.36"
    MAX_WORKERS: int = 20
    TIMEOUT: int = 10

config = Config()