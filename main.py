
from __future__ import annotations
from typing import *
import os, sys
from getopt import gnu_getopt
import openai
from openai.types.chat import ChatCompletion
import pathlib
import re
from dataclasses import dataclass
import enum

class IssueKind(enum.Enum):
    BAD_NAME = enum.auto()
    BAD_COMMENT = enum.auto()
    BAD_DOCUMENTATION = enum.auto()
    DUPLICATE_CODE = enum.auto()
    EXPOSED_IMPLEMENTATION_DETAIL = enum.auto()
    UNNECESSARILY_DETAILED_DEPENDENCY = enum.auto()
    MULTIPLE_RESPONSIBILITIES = enum.auto()
    BAD_SUBTYPE = enum.auto()
    UNCHECKED_INPUT = enum.auto()

class ConstructKind(enum.Enum):
    TOP_LEVEL = enum.auto()
    FUNCTION = enum.auto()
    VARIABLE = enum.auto()
    TYPE = enum.auto()

@dataclass(frozen=True, eq=True)
class IssueLocation:
    nested: Optional[IssueLocation]
    kind: ConstructKind
    identifier: str

    def __str__(self) -> str:
        me = f"{self.kind.name.lower()}:{self.identifier}"
        return f"{me}/{self.nested}" if self.nested is not None else me

@dataclass(frozen=True, eq=True)
class IssueInstanceKey:
    kind: IssueKind
    file: str
    location: IssueLocation

@dataclass(frozen=True)
class IssueInstance:
    key: IssueInstanceKey
    severity: int
    description: Optional[str]

def walk(path: str):
    for entry in os.scandir(path):
        if entry.is_file():
            yield pathlib.Path(entry.path)
        elif entry.is_dir():
            yield from walk(entry.path)

def indent(text: str):
    return "\n".join(f"{i+1: <8}{line}" for i, line in enumerate(text.split("\n")))

def parse_issue_location(part: str) -> IssueLocation:
    slash_index = part.find("/")
    of_interest = (part[:slash_index] if slash_index >= 0 else part).split(":")
    assert len(of_interest) == 2
    return IssueLocation(
        kind=ConstructKind[of_interest[0].upper()],
        identifier=of_interest[1],
        nested=parse_issue_location(part[slash_index + 1:]) if slash_index >= 0 else None
    )

def parse_issue_instance(line: str) -> IssueInstance:
    split = line.split("|")
    assert len(split) == 4 or len(split) == 5
    return IssueInstance(
        key=IssueInstanceKey(
            kind=IssueKind[split[2].upper()],
            file=split[0],
            location=parse_issue_location(split[1]),
        ),
        severity=int(split[3]),
        description=split[4] if len(split) >= 4 else None
    )

def main(argv: List[str]):
    # parse_issue_instance("config.py|type:Config/variable:log_file|bad_name|1|Consider replacing 'log_file' with a more descriptive name.")
    # return
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
        { "role": "system", "content": pathlib.Path(__file__).parent.joinpath("mvp2.md").read_text() },
        { "role": "user", "content": "\n".join(f"{path}:\n{indent(content)}" for path, content in contents) },
    ], model="gpt-4", n=10)

    votes: Dict[IssueInstanceKey, List[IssueInstance]] = {}
    voter_issues: List[int] = []
    for choice in result.choices:
        smell_instances: List[IssueInstance] = []
        for line in choice.message.content.split("\n"):
            if line.strip() == "@done":
                break
            try:
                smell_instances.append(parse_issue_instance(line))
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
        print(f"{key.file}#{key.location}, {key.kind.name.lower()} ({n_votes} votes, avg. severity {avg_severity:.2f}):")
        for vote in votes[key]:
            if vote.description is not None:
                print(f"   {vote.description}")

if __name__ == "__main__":
    main(sys.argv[1:])
    pass