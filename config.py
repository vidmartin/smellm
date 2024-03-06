
from typing import *
from dataclasses import dataclass, field
from getopt import gnu_getopt
import pathlib

@dataclass(eq=True, frozen=True)
class Config:
    n: int = 5
    min_vote_share: float = 0.5
    log_file: pathlib.Path = field(default_factory=lambda: pathlib.Path("log.txt"))

def get_args_and_config(argv: List[str]):
    opts, args = gnu_getopt(argv, "", ["n=", "min-vote-share=", "log-file="])
    opts_d: Dict[str, Any] = { k[2:].replace("-", "_"): v for k, v in opts }
    opts_d = { k: Config.__annotations__[k](v) for k, v in opts_d.items() }
    return Config(**opts_d), args
