import logging
import sys
from datetime import datetime


def initialize_logs():
    datetime_now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(f"revisur_log_run_{datetime_now}.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    class StreamToLogger:
        def __init__(self, log_level):
            self.log_level = log_level
            self.linebuf = ""

        def write(self, buf):
            for line in buf.rstrip().splitlines():
                logging.log(self.log_level, line.rstrip())

        def flush(self):
            pass

    sys.stdout = StreamToLogger(logging.INFO)
    sys.stderr = StreamToLogger(logging.ERROR)
