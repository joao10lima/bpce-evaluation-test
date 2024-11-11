import logging
import os
import pathlib
import shutil
import signal
import sys
import threading
from datetime import datetime

import cv2
import mss
import numpy as np


class Video:
    """
    This class control the video record which happens
    on separate thread and is responsible for defining
    video format and their folders.
    """

    def __init__(self, driver):
        """The video class initializes by
        defining the captures path and
        the thread to be open.

        Args:
            driver (driver): selenium driver
        """
        datetime_now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.path = pathlib.Path("captures/")
        self.screenshot_path = pathlib.Path("screenshots/")
        self.output_filename = f"captures/screen_capture_{datetime_now}.avi"
        self.screenshot_count = 0
        self.stop_recording_event = threading.Event()
        self.record_thread = threading.Thread(
            target=self.record_screen, args=(self.stop_recording_event,)
        )
        self.driver = driver
        self.clean_up()

    def clean_up(self):
        """At the start of each execution we must
        clean the the screenshot path since is from them
        we do comparisons
        """
        self.path.mkdir(parents=True, exist_ok=True)
        shutil.rmtree(str(self.screenshot_path))
        self.screenshot_path.mkdir(parents=True, exist_ok=True)

    def record_screen(self, stop_recording_event):
        """With MSS lib we take machine monitor
        default dimensions to define the video size.
        After since we are in thread we run until
        the event passed is false.

        To construct the video we take Selenium screenshots
        for each frame. The interesting part is that we can do
        that even in the headless mode.

        Args:
            stop_recording_event (thread_event): is a passed
            event which indicates that the recording must stop
        """
        self.screen = mss.mss()
        monitor = self.screen.monitors[1]
        out = cv2.VideoWriter(
            self.output_filename,
            cv2.VideoWriter_fourcc(*"XVID"),
            20.0,
            (monitor["width"], monitor["height"]),
        )
        try:
            while not stop_recording_event.is_set():
                screenshot = self.driver.get_screenshot_as_png()
                frame = cv2.imdecode(
                    np.frombuffer(screenshot, np.uint8), cv2.IMREAD_COLOR
                )
                frame_resized = cv2.resize(
                    frame, (monitor["width"], monitor["height"])
                )
                out.write(frame_resized)
        finally:
            out.release()

    def start_screen_rec(self):
        """Initiates the thread but before
        add a signal handler so we can terminate
        with a Ctrl+c
        """

        def signal_handler(sig, frame):
            """Handle the signal to force
            the event closure.

            Args:
                sig (int): int of the signal received
                frame (exec): frame
            """
            logging.info("\nCtrl+C detected! Exiting...")
            self.stop_recording_event.set()
            sys.exit(1)

        signal.signal(signal.SIGINT, signal_handler)

        self.record_thread.start()

    def end_screen_record(self, persist_video=False):
        """Here we send the event to close the thread
        recording the video.

        Args:
            persist_video (bool, optional): If the execution did not
        give any errors we discard the video file. Defaults to False.
        """
        self.stop_recording_event.set()
        self.record_thread.join()

        if not persist_video:
            logging.info("Deleting file: " + self.output_filename)
            os.remove(self.output_filename)

        logging.info("Recording stopped.")
