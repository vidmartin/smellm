
from __future__ import annotations
from typing import *
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
