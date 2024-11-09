import os
import subprocess
import sys
import time

import win32con
import win32gui

from config.settings import Settings

# Suppress only DeprecationWarnings
# See: https://github.com/glitchassassin/lackey/issues/127
sys.stderr = open(os.devnull, "w")
import lackey

sys.stderr = sys.__stderr__


def open_browser(settings: Settings):
    browser_paths = {
        "chrome": settings.chrome_path,
        "edge": settings.edge_path,
    }

    full_command = [
        browser_paths.get(settings.default_browser),
        "--incognito",
        "--start-maximized",
        "--user-data-dir=c:\\temp",
    ]
    # Launch the browser
    if settings.default_browser == "chrome" or settings.default_browser == "edge":
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
            if settings.default_browser.lower() in window_title.lower():
                # Bring the window to the foreground and maximize
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                win32gui.SetForegroundWindow(hwnd)

        win32gui.EnumWindows(enum_windows, None)

    # Set the last opened browser window to foreground and maximize it
    set_foreground_window()


def type_enter(text):
    lackey.type(text)
    lackey.type("{ENTER}")
    time.sleep(2)


def click_page(target):
    try:
        time.sleep(4)
        lackey.click(target)
    except lackey.Exceptions.FindFailed:
        print(f"TARGET {target} NOT FOUND.")
        return False
    return True


def reset_mouse_pos():
    # Get the center position of the screen
    center_position = lackey.Screen().getCenter()

    # Move the mouse to the center position
    lackey.mouseMove(center_position)


def search_scroll(target_image):
    scrolling = True

    # Reset mouse to center preparing for scrolling
    reset_mouse_pos()

    # Reduce timeout for faster scrolling
    lackey.setAutoWaitTimeout(0.1)
    while scrolling:
        try:
            target_region = lackey.find(target_image)
            print("Component found at:", target_region)
            # Returning speed to default
            lackey.setAutoWaitTimeout(3)
            return target_region
        except lackey.FindFailed:
            # If not found, scroll down and try again
            print("Component not found, scrolling down...")
            # Scroll down 1 steps
            lackey.wheel(None, lackey.Mouse.WHEEL_DOWN, 5)


def close_running_window():
    time.sleep(5)
    lackey.keyDown("{ALT}")  # Press and hold Alt
    lackey.type("{F4}")  # Press F4 while Alt is held down
    lackey.keyUp("{ALT}")  # Release Alt


def main():

    settings = Settings("param.xml")
    open_browser(settings)

    type_enter("www.banquepopulaire.fr")
    click_page(settings.tout_accepter)
    search_scroll(settings.trouver_une_agence)
    click_page(settings.trouver_une_agence)

    click_page(settings.rue_type)
    lackey.type("Lyon")
    click_page(settings.code_postal)
    lackey.type("69000")

    click_page(settings.rechercher_click)
    click_page(settings.lyon_perrache)

    lackey.find(settings.cinq_agences_banque)
    click_page(settings.quatre_quatre)
    lackey.find(settings.quatre_detail)

    close_running_window()
    print("script completed.")


if __name__ == "__main__":
    main()
