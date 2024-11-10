import os
import subprocess
import sys
import time
from pathlib import Path

import win32con
import win32gui

from reviseur.settings import Settings
from reviseur.video import Video

# Suppress only DeprecationWarnings
# See: https://github.com/glitchassassin/lackey/issues/127
sys.stderr = open(os.devnull, "w")
import lackey

sys.stderr = sys.__stderr__


class Reviseur:

    def __init__(self, settings, video: Video):
        self.settings = settings
        # Atributing here in case we need further configuration
        self.lackey: lackey = lackey
        self.video = video

    def open_browser(self):
        browser_paths = {
            "chrome": self.settings.chrome_path,
            "edge": self.settings.edge_path,
        }

        full_command = [
            browser_paths.get(self.settings.default_browser),
            (
                "--incognito"
                if self.settings.default_browser == "chrome"
                else "--inprivate"
            ),
        ]
        # Launch the browser
        if (
            self.settings.default_browser == "chrome"
            or self.settings.default_browser == "edge"
        ):
            subprocess.Popen(full_command)
        else:
            raise Exception("Browser not supported!")

        # Wait for the browser to open
        time.sleep(2)

        # Function to bring the last opened browser window to the foreground and maximize
        def set_foreground_window():
            def enum_windows(hwnd, _):
                # Get the title of the window
                window_title = win32gui.GetWindowText(hwnd)
                # Check if the window title matches the browser name
                full_browser_name = {
                    "edge": "Microsoft Edge",
                    "chrome": "Google Chrome",
                    "firefox": "Firefox",
                }
                if (
                    full_browser_name[self.settings.default_browser].lower()
                    in window_title.lower()
                ):
                    # Bring the window to the foreground and maximize
                    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                    win32gui.SetForegroundWindow(hwnd)

            win32gui.EnumWindows(enum_windows, None)

        # Set the last opened browser window to foreground and maximize it
        set_foreground_window()

    def type_enter(self, text):
        self.lackey.type(text)
        self.lackey.type("{ENTER}")
        time.sleep(2)
        self.video.write_frame(self.video.save_screenshot(f"type_{text[:5]}"))

    def click_page(self, target):
        target_stem = Path(target).stem
        try:
            time.sleep(5)
            self.video.write_frame(
                self.video.save_screenshot(f"click_page_{target_stem}_1")
            )
            self.lackey.click(target)
            self.video.write_frame(
                self.video.save_screenshot(f"click_page_{target_stem}_2")
            )
        except self.lackey.Exceptions.FindFailed:
            print(f"TARGET {target} NOT FOUND.")
            return False
        return True

    def reset_mouse_pos(self):
        # Move the mouse to the center position
        self.lackey.mouseMove(self.lackey.Screen().getCenter())

    def search_scroll(self, target_image):
        scrolling = True
        target_stem = Path(target_image).stem

        # Reset mouse to center preparing for scrolling
        self.reset_mouse_pos()

        iteration_count = 0
        # Reduce timeout for faster scrolling
        self.lackey.setAutoWaitTimeout(0.1)
        while scrolling:
            try:
                target_region = self.lackey.find(target_image)
                print("Component found at:", target_region)
                # Returning speed to default
                self.lackey.setAutoWaitTimeout(3)
                self.video.write_frame(self.video.save_screenshot(target_stem))
                return target_region
            except self.lackey.FindFailed:
                # If not found, scroll down and try again
                print("Component not found, scrolling down...")
                # Scroll down 1 steps
                self.lackey.wheel(None, self.lackey.Mouse.WHEEL_DOWN, 5)
                self.video.write_frame(self.video.capture_screen())
            iteration_count += 1

    def close_running_window(self):
        time.sleep(3)
        self.lackey.keyDown("{ALT}")  # Press and hold Alt
        self.lackey.type("{F4}")  # Press F4 while Alt is held down
        self.lackey.keyUp("{ALT}")  # Release Alt

    def workflow_banque_populaire(self):
        settings = Settings("param.xml")
        self.open_browser()

        self.type_enter("www.banquepopulaire.fr")
        self.click_page(self.settings.tout_accepter)
        self.search_scroll(self.settings.trouver_une_agence)
        self.click_page(self.settings.trouver_une_agence)

        self.click_page(self.settings.rue_type)
        self.lackey.type("Lyon")
        self.video.write_frame(self.video.save_screenshot(f"type_Lyon"))
        self.click_page(self.settings.code_postal)
        self.lackey.type("69000")
        self.video.write_frame(self.video.save_screenshot(f"type_69000"))

        self.click_page(self.settings.rechercher_click)
        self.click_page(self.settings.lyon_perrache)

        self.lackey.find(self.settings.cinq_agences_banque)
        self.video.write_frame(self.video.save_screenshot(f"find_cinq_agences_banque"))
        self.click_page(self.settings.quatre_quatre)
        self.lackey.find(settings.quatre_detail)
        self.video.write_frame(self.video.save_screenshot(f"find_quatre_detail"))
        self.close_running_window()
        self.video.end_record()
        print("script completed.")
