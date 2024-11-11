import logging
import pathlib
import sys
from datetime import datetime


def initialize_logs():
    """Initialize logs and save to the folder logs/
    also make sure to write all errors and infos.
    """
    pathlib.Path("logs/").mkdir(parents=True, exist_ok=True)
    datetime_now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(f"logs/revisur_log_run_{datetime_now}.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    class StreamToLogger:
        """Make sure to write log
        following the previous config
        """

        def __init__(self, log_level):
            """Initializes StremToLogger

            Args:
                log_level (log.LEVEL): INFO or DEBUG
            """
            self.log_level = log_level
            self.linebuf = ""

        def write(self, buf):
            """Write the corresponding
            buffer according to the log rules

            Args:
                buf (buffer): text to be written
            """
            for line in buf.rstrip().splitlines():
                logging.log(self.log_level, line.rstrip())

        def flush(self):
            """Flush the log writing"""
            pass

    sys.stdout = StreamToLogger(logging.INFO)
    sys.stderr = StreamToLogger(logging.ERROR)
