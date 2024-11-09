
import subprocess
import lackey
import time
import os

from config.setttings import Settings

start_icon = "start_icon.PNG"
tout_accepter = "tout_accepter.PNG"
trover_une_agence = "trover_une_agence.PNG"
rue = "rue.PNG"
code_postal = "code_postal.PNG"

# FUNCTION TO OPEN BROWSER
# GENERIC FUNCTION FOR CLICK AND ENTER
# HANDLE ERRORS
# FUNCTION SEARCH ELEMENT ON THE ENTIRE PAGE(SCROLL ALL)


def open_default_browser(settings):
    """
    Opens the default browser from settings, using private mode if cookies are not to be stored.
    """
    browser_paths = {
        "chrome": (settings.chrome_path, "--incognito"),
        "edge": (settings.edge_path, "--inprivate"),
        "firefox": (settings.firefox_path, "-private-window")
    }

    browser_path, private_flag = browser_paths.get(settings.default_browser, (None, None))

    if not browser_path or not os.path.exists(browser_path):
        print("Default browser path not found or does not exist.")
        return

    # Add private mode flag if cookies are not to be stored
    args = [browser_path] + ([private_flag] if not settings.store_browser_cookies else [])
    
    try:
        subprocess.Popen(["cmd", "/c", "start", "", *args], shell=True)
        print(f"Opened {settings.default_browser} browser{' in private mode' if private_flag in args else ''}.")
    except Exception as e:
        print(f"Failed to open the browser: {e}")

def type_enter(text):
    lackey.type(text)
    lackey.type("{ENTER}")
    time.sleep(2)

def click_page(target):
    try:
        lackey.click(target)
        time.sleep(2)
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
            lackey.wheel(None, lackey.Mouse.WHEEL_DOWN, 1)
    


if __name__ == "__main__":
    settings = Settings('param.xml')
    open_default_browser(settings)

    type_enter("https://www.banquepopulaire.fr/")
    click_page(settings.tout_accepter)
    search_scroll(settings.trover_une_agence)
    click_page(settings.trover_une_agence)

    click_page(settings.rue_type)
    lackey.type("Lyon")
    click_page(settings.code_postal)
    lackey.type("69000")

    print("script completed.")

