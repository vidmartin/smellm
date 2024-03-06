
from __future__ import annotations
from typing import *
import os, sys
from getopt import gnu_getopt
import openai
from openai.types.chat import ChatCompletion
import pathlib
import re
import response
import config
import logger
from dataclasses import dataclass

def walk(path: str):
    for entry in os.scandir(path):
        if entry.is_file():
            yield pathlib.Path(entry.path)
        elif entry.is_dir():
            yield from walk(entry.path)

def indent(text: str):
    return "\n".join(f"    {line}" for i, line in enumerate(text.split("\n")))

def main(argv: List[str]):
    # parse_issue_instance("config.py|type:Config/variable:log_file|bad_name|1|Consider replacing 'log_file' with a more descriptive name.")
    # return
    cfg, args = config.get_args_and_config(argv)
    log = logger.Logger(
        cfg.log_file if cfg.log_file.is_absolute() else pathlib.Path(__file__).parent.joinpath(cfg.log_file)
    )
    client = openai.Client(api_key=os.environ["OPENAI_API_KEY"])

    log.log(" -> reading source codes", True)
    contents = [
        (path, path.read_text())
        for path in walk(".")
        if any(path.match(pattern) for pattern in args)
    ]

    if not contents:
        log.log(" -> no files found, exiting", True)
        return

    log.log(" -> communicating with LLM", True)
    result: ChatCompletion = client.chat.completions.create(messages=[
        { "role": "system", "content": pathlib.Path(__file__).parent.joinpath("mvp2.md").read_text() },
        { "role": "user", "content": "\n".join(f"{path}:\n{indent(content)}" for path, content in contents) },
    ], model="gpt-4", n=cfg.n)

    votes: Dict[response.IssueInstanceKey, List[response.IssueInstance]] = {}
    issues_by_voter: List[List[response.IssueInstance]] = []
    for choice in result.choices:
        issue_instances: List[response.IssueInstance] = []
        for line in choice.message.content.split("\n"):
            if line.strip() == "@done":
                break
            try:
                issue_instances.append(response.parse_issue_instance(line))
            except Exception as err:
                log.log(f" -> wrong output format: '{line}' (see log file for details)", True)
                log.log(str(err), False)
                continue
        
        for issue_instance in issue_instances:
            if issue_instance.key not in votes:
                votes[issue_instance.key] = []
            votes[issue_instance.key].append(issue_instance)
        
        issues_by_voter.append(issue_instances)

    log.log(f"\nRESULT:", True)
    log.log(f"{sum(1 for issues in issues_by_voter if len(issues) == 0)} voters were impressed (had no issues)", True)
    log.log(f"{sum(1 for issues in issues_by_voter if all(issue.severity <= 2 for issue in issues))} voters were happy (had no issues with severity greater than 2)", True)
    log.log(f"{result.usage.total_tokens} tokens used in total", True)
    log.log("notable detections:", True)
    for key in sorted(votes.keys(), key=lambda k: len(votes[k]), reverse=True):
        n_votes = len(votes[key])
        display = n_votes >= cfg.min_vote_share * cfg.n
        avg_severity = sum(vote.severity for vote in votes[key]) / n_votes
        log.log(f"  - in file '{key.file}' at {key.location}: {key.kind.name.lower()} ({n_votes} votes, avg. severity {avg_severity:.2f}):", display)
        for vote in votes[key]:
            if vote.description is not None:
                log.log(f"     - {vote.description}", display)

if __name__ == "__main__":
    main(sys.argv[1:])
