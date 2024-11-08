
import lackey
import time

start_icon = "start_icon.PNG"
tout_accepter = "tout_accepter.PNG"
trover_une_agence = "trover_une_agence.PNG"
rue = "rue.PNG"
code_postal = "code_postal.PNG"

# FUNCTION TO OPEN BROWSER
# GENERIC FUNCTION FOR CLICK AND ENTER
# HANDLE ERRORS
# FUNCTION SEARCH ELEMENT ON THE ENTIRE PAGE(SCROLL ALL)


def open_firefox():
    lackey.click(start_icon)
    time.sleep(2)

    lackey.type("firefox")
    lackey.type("{ENTER}")
    time.sleep(2)

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

def search_scroll(target_image):
    found = False
    previous_position = None
    scrolling = True

    while scrolling:
        try:
            target_region = lackey.find(target_image)
            print("Component found at:", target_region)
            found = True  # Set the flag to indicate the component was found

            # Perform an action after locating the component
            lackey.click(target_region)  # For example, click on the component
            scrolling = False  # Stop scrolling if the component is found
            break  # Exit the loop if found

        except lackey.FindFailed:
            # If not found, scroll down and try again
            print("Component not found, scrolling down...")

            # Scroll down 5 steps
            lackey.wheel(None, lackey.WHEEL_DOWN, 5)
            time.sleep(1)  # Small delay to allow the screen to update

            # Track scroll position (use screen height or other logic)
            current_position = lackey.Screen().getBounds().height

            # Check if the position has changed; if not, we are at the bottom of the page
            if current_position == previous_position:
                print("Reached the bottom of the page, no more content to load.")
                scrolling = False  # Stop scrolling if the bottom is reached

            # Update the previous position
            previous_position = current_position


if __name__ == "__main__":
    open_firefox()
    type_enter("https://www.banquepopulaire.fr/")
    click_page(tout_accepter)
    search_scroll(trover_une_agence)
    lackey.click(trover_une_agence)
    time.sleep(2)

    lackey.click(rue)
    lackey.type("Lyon")
    time.sleep(2)


    lackey.click(code_postal)
    lackey.type("69000")
    time.sleep(2)
    print("script completed.")

