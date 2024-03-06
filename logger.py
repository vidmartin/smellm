
import datetime

class Logger:
    def __init__(self, log_file: str):
        self._log_file = log_file

    def log(self, message: str, stdout: bool):
        with open(self._log_file, "a") as file:
            print(f"{datetime.datetime.now().isoformat()}:{message}", file=file)
        if stdout:
            print(message)
