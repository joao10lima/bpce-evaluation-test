import pathlib
from datetime import datetime

import cv2
import numpy as np
import win32api
import win32con
import win32gui
import win32ui


class Video:
    def __init__(self, fps=1):
        datetime_now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        pathlib.Path("captures/").mkdir(parents=True, exist_ok=True)
        self.output_filename = f"captures/screen_capture_{datetime_now}.mp4"
        self.screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        self.screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        self.screen_size = (self.screen_width, self.screen_height)
        self.fps = fps
        self.screenshot_count = 0

        self.out = cv2.VideoWriter(
            self.output_filename,
            cv2.VideoWriter_fourcc(*"mp4v"),
            self.fps,
            self.screen_size,
        )

    def capture_screen(self):
        hwin = win32gui.GetDesktopWindow()
        hwindc = win32gui.GetWindowDC(hwin)
        srcdc = win32ui.CreateDCFromHandle(hwindc)
        memdc = srcdc.CreateCompatibleDC()

        # Create a bitmap to hold the screenshot
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(srcdc, self.screen_width, self.screen_height)
        memdc.SelectObject(bmp)
        memdc.BitBlt(
            (0, 0),
            (self.screen_width, self.screen_height),
            srcdc,
            (0, 0),
            win32con.SRCCOPY,
        )

        # Convert the bitmap to a numpy array for OpenCV
        bmp_info = bmp.GetInfo()
        bmp_data = bmp.GetBitmapBits(True)
        img = np.frombuffer(bmp_data, dtype=np.uint8)
        img.shape = (bmp_info["bmHeight"], bmp_info["bmWidth"], 4)

        # Convert the image from BGRA to BGR for OpenCV compatibility
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # Release resources
        memdc.DeleteDC()
        win32gui.ReleaseDC(hwin, hwindc)
        win32gui.DeleteObject(bmp.GetHandle())

        return frame

    def save_screenshot(self, filename):
        frame = self.capture_screen()
        pathlib.Path("screenshots/").mkdir(parents=True, exist_ok=True)
        cv2.imwrite(
            "screenshots/" + f"{self.screenshot_count}_" + filename + ".png", frame
        )
        print(f"Screenshot saved as {filename}")
        self.screenshot_count += 1
        return frame

    def write_frame(self, frame):
        self.out.write(frame)

    def end_record(self):
        self.out.release()
        cv2.destroyAllWindows()
