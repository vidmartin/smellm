
from typing import *
import os, sys
from getopt import gnu_getopt
import openai
from openai.types.chat import ChatCompletion
import pathlib
import re
from dataclasses import dataclass
import enum

class SmellKind(enum.Enum):
    BAD_NAME = enum.auto()
    BAD_COMMENT = enum.auto()
    BAD_DOCUMENTATION = enum.auto()
    DUPLICATE_CODE = enum.auto()
    EXPOSED_IMPLEMENTATION_DETAIL = enum.auto()
    UNNECESSARILY_DETAILED_DEPENDENCY = enum.auto()
    MULTIPLE_RESPONSIBILITIES = enum.auto()
    BAD_SUBTYPE = enum.auto()

@dataclass(frozen=True, eq=True)
class SmellInstanceKey:
    kind: SmellKind
    file: str
    line: int

@dataclass(frozen=True)
class SmellInstance:
    key: SmellInstanceKey
    severity: int
    suggestion: Optional[str]

def walk(path: str):
    for entry in os.scandir(path):
        if entry.is_file():
            yield pathlib.Path(entry.path)
        elif entry.is_dir():
            yield from walk(entry.path)

def indent(text: str):
    return "\n".join(f"{i+1: <8}{line}" for i, line in enumerate(text.split("\n")))

def parse_smell_instance(line: str) -> SmellInstance:
    match = re.match(r"^([\w.\-\/]+)#(\d+), ([\w.\-\/]+)\/(\d+)(: .*)?$", line)
    if not match:
        raise ValueError
    return SmellInstance(
        key=SmellInstanceKey(
            kind=SmellKind[match.group(3).upper()],
            file=match.group(1),
            line=int(match.group(2)),
        ),
        severity=int(match.group(4)),
        suggestion=match.group(5)[2:]
    )

def main(argv: List[str]):
    opts, args = gnu_getopt(argv, "", [])
    client = openai.Client(api_key=os.environ["OPENAI_API_KEY"])

    print("reading source codes")
    contents = [
        (path, path.read_text())
        for path in walk(".")
        if any(path.match(pattern) for pattern in args)
    ]

    if not contents:
        print("no files found")
        return

    print("communicating with LLM")
    result: ChatCompletion = client.chat.completions.create(messages=[
        { "role": "system", "content": pathlib.Path(__file__).parent.joinpath("mvp.md").read_text() },
        { "role": "user", "content": "\n".join(f"{path}:\n{indent(content)}" for path, content in contents) },
    ], model="gpt-4", n=10)

    votes: Dict[SmellInstanceKey, List[SmellInstance]] = {}
    voter_issues: List[int] = []
    for choice in result.choices:
        smell_instances: List[SmellInstance] = []
        for line in choice.message.content.split("\n"):
            if line.strip() == "done":
                break
            try:
                smell_instances.append(parse_smell_instance(line))
            except Exception as _err:
                print(f"wrong output format: '{line}'")
                continue
        
        for smell_instance in smell_instances:
            if smell_instance.key not in votes:
                votes[smell_instance.key] = []
            votes[smell_instance.key].append(smell_instance)
        
        voter_issues.append(len(smell_instances))

    print(f"\nRESULT ({sum(1 for n_issues in voter_issues if n_issues == 0)} voters had no issues):")
    for key in sorted(votes.keys(), key=lambda k: len(votes[k]), reverse=True):
        n_votes = len(votes[key])
        avg_severity = sum(vote.severity for vote in votes[key]) / n_votes
        print(f"{key.file}#{key.line}, {key.kind.name.lower()} ({n_votes} votes, avg. severity {avg_severity:.2f}):")
        for vote in votes[key]:
            print(f"   {vote.suggestion}")

if __name__ == "__main__":
    main(sys.argv[1:])
    pass