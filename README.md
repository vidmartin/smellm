
# smeLLM

A simple Python tool for detecting code smells and signs of bad design in code. Uses GPT-4, expects the OpenAI API key to be located in the `OPENAI_API_KEY` environment variable.

## Usage examples

Evaluate all Python and JavaScript files in the current directory or any of its subdirectories (recursively) with default parameters:

    python main.py '*.py' '*.js'

Evaluate all Python files in the current directory, but have the LLM only generate one response:

    python main.py '*.py' --n=1

Evaluate all Python files in the current directory, but have the LLM generate 10 responses, and only display the issues that were detected in at least by 7 of those 10 responses in the console:

    python main.py '*.py' --n=10 --min-vote-share=0.7

## Available options with defaults

- `--n=5`: the `n` parameter used when communicating with the OpenAI chat completions API, corresponds to the number of different responses they generate.
- `--min-vote-share=0.5`: the minimum share of votes an issue needs to have to be written to STDOUT. A vote is seen as an occurence of a particular issue (at a particular place, of a particular type) in a particular response. So for `n=5`, an issue might have up to 5 votes. 
- `--log-file=log.txt`: the log file to which we will write things. Everything that is written to STDOUT is also written to this file, but with greater level of detail. For example, ALL issues with at least 1 vote are written to this file, regardless of the `--min-vote-share` option, unlike for STDOUT, where the `--min-vote-share` option matters.

## Prompt engineering

The system prompt that is used is located in the `mvp2.md` file. I am not happy with the results yet, further experimantation with the content of this file would be needed.
