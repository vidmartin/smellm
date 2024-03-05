
from dataclasses import dataclass

@dataclass(eq=True, frozen=True)
class Config:
    n: int = 5
    min_vote_share: float = 0.5
    log_file: str = "log.txt"
    
