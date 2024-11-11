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
    def __init__(self, driver):
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
        self.path.mkdir(parents=True, exist_ok=True)
        shutil.rmtree(str(self.screenshot_path))
        self.screenshot_path.mkdir(parents=True, exist_ok=True)

    def record_screen(self, stop_recording_event):
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

    def save_screenshot(self, filename):
        screen = mss.mss()
        monitor = screen.monitors[1]
        screenshot = screen.grab(monitor)
        cv2.imwrite(
            "screenshots/" + f"{self.screenshot_count}_" + filename + ".png",
            np.array(screenshot),
        )
        pathlib.Path("screenshots/").mkdir(parents=True, exist_ok=True)
        self.path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Screenshot saved as {filename}")
        self.screenshot_count += 1

    def start_screen_rec(self):
        def signal_handler(sig, frame):
            logging.info("\nCtrl+C detected! Exiting...")
            self.stop_recording_event.set()
            sys.exit(1)

        signal.signal(signal.SIGINT, signal_handler)

        self.record_thread.start()

    def end_screen_record(self, persist_video=False):
        self.stop_recording_event.set()
        self.record_thread.join()

        if not persist_video:
            logging.info("Deleting file: " + self.output_filename)
            os.remove(self.output_filename)

        logging.info("Recording stopped.")
