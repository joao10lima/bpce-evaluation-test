import logging
import os
import pathlib
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service

from reviseur.report import Report
from reviseur.settings import Settings
from reviseur.video import Video

# Suppress only DeprecationWarnings
# See: https://github.com/glitchassassin/lackey/issues/127
sys.stderr = open(os.devnull, "w")
import lackey  # noqa: E402

sys.stderr = sys.__stderr__


class Reviseur:
    """Most important class that manages
    the selenium driver and has an algorithm
    of comparison between the images defined
    in the XML against the ones saved by
    the browser driver itself.
    """

    def __init__(self, settings):
        """Initiates the reviseur class by
        defining the settings and lackey
        functions.

        Args:
            settings (Settings): Settings from the XML
        """
        self.settings: Settings = settings
        pathlib.Path("screenshots/").mkdir(parents=True, exist_ok=True)
        # Atributing here in case we need further configuration
        self.lackey: lackey = lackey

    def click_element(self, element):
        """Click the element and wait
        a time before returning

        Args:
            element (driver): driver element
        """
        element.click()
        time.sleep(1)

    def lackey_compare(self, expected, actual, threshold=0.9):
        """This function is based on the following article:
        https://docs.opencv.org/3.4/d4/dc6/tutorial_py_template_matching.html

        With this we can receive images from the xml and check them
        against the full screen renderization of the selenium driver

        It is configurable with a threshold that indicate the differece
        between the images.

        So it functions like an assert() if not asserted them
        e generate a report and video.

        Args:
            expected (str): path to image from the .xml
            actual (str): path to image generate by selenium
            threshold (float, optional): algorithm threshold.

        Raises:
            Exception: Image is not compatible to what the driver sees
        """
        template = cv2.imread(expected, 0)
        actual = cv2.imread(actual, 0)

        if (
            template.shape[0] > actual.shape[0]
            or template.shape[1] > actual.shape[1]
        ):
            scale_factor = min(
                actual.shape[0] / template.shape[0],
                actual.shape[1] / template.shape[1],
            )
            template = cv2.resize(
                template, (0, 0), fx=scale_factor, fy=scale_factor
            )

        template = template[: actual.shape[0], : actual.shape[1]]
        difference = cv2.matchTemplate(actual, template, cv2.TM_CCOEFF_NORMED)

        loc = np.where(difference >= threshold)
        logging.info(f"{self.step} Difference Score of: {len(loc[0])}")
        if len(loc[0]) > 100:
            logging.info(
                "Expected image don't match actual page! Preparing Report..."
            )
            raise Exception("Inconsistency")

    def step_tout_acepter(self, driver):
        """First step accept the cookie warning

        Args:
            driver: Selenium Driver
        """
        self.step = "1_tout_acepter"
        driver.get("https://www.banquepopulaire.fr")
        driver.save_screenshot("screenshots/tout_acepter_before_click.png")
        self.lackey_compare(
            self.settings.tout_accepter,
            "screenshots/tout_acepter_before_click.png",
        )

    def step_consent_prompt_submit(self, driver):
        """Second step click the consent prompt

        Args:
            driver: Selenium Driver
        """
        self.step = "2_consent_prompt_submit"
        consent_prompt_submit = driver.find_element(
            By.ID, "consent_prompt_submit"
        )
        self.click_element(consent_prompt_submit)

    def step_trouver_une_agence(self, driver):
        """Third step scroll to an element
        then click in them

        Args:
            driver: Selenium Driver
        """
        self.step = "3_trouver_une_agence"
        agence = driver.find_element(
            By.XPATH,
            "//p[@class='font-text-body-bold']"
            + "[normalize-space()='Trouver une agence']",
        )
        actions = ActionChains(driver)
        actions.move_to_element(agence).perform()
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(1)
        driver.save_screenshot("screenshots/trouver_une_agence_click.png")
        self.lackey_compare(
            self.settings.trouver_une_agence,
            "screenshots/trouver_une_agence_click.png",
        )
        self.click_element(agence)

    def step_rue_search(self, driver):
        """Fourth step type the name of
        the street

        Args:
            driver: Selenium Driver
        """
        self.step = "4_rue_search"
        rue_search = driver.find_element(By.ID, "em-search-form__searchstreet")
        self.click_element(rue_search)
        rue_search.send_keys("Lyon")
        driver.save_screenshot("screenshots/type_rue_search.png")
        self.lackey_compare(
            self.settings.rue_type,
            "screenshots/type_rue_search.png",
        )

    def step_code_postal(self, driver):
        """Fifth step type the postal code

        Args:
            driver: Selenium Driver
        """
        self.step = "5_code_postal"
        code_postal = driver.find_element(By.ID, "em-search-form__searchcity")
        self.click_element(code_postal)
        code_postal.send_keys("69000")
        driver.save_screenshot("screenshots/type_code_postal.png")
        self.lackey_compare(
            self.settings.code_postal,
            "screenshots/type_code_postal.png",
        )

    def step_submit_addr(self, driver):
        """Sixth step click on the rechercher
        button

        Args:
            driver: Selenium Driver
        """
        self.step = "6_submit_addr"
        submit_addr = driver.find_element(
            By.XPATH,
            '//*[@id="em-search-form"]/div/div[2]/fieldset[2]/div[2]/button',
        )
        self.click_element(submit_addr)
        driver.save_screenshot("screenshots/rechercher_click.png")
        self.lackey_compare(
            self.settings.rechercher_click,
            "screenshots/rechercher_click.png",
        )

    def step_geocoder(self, driver):
        """Seventh click on the right
        address in the list

        Args:
            driver: Selenium Driver
        """
        self.step = "7_geocoder"
        geocoder = driver.find_element(
            By.XPATH, '//*[@id="cgeocoder29_street_1"]'
        )
        self.click_element(geocoder)
        time.sleep(8)
        driver.save_screenshot("screenshots/find_cinq_agences_banque.png")
        self.lackey_compare(
            self.settings.cinq_agences_banque,
            "screenshots/find_cinq_agences_banque.png",
        )

    def step_quatre_detail(self, driver):
        """Eighth step hover the mouse
        over the quatre image and check
        if new content is loaded

        Args:
            driver: Selenium Driver
        """
        self.step = "8_quatre_detail"
        quatre_detail = driver.find_element(
            By.XPATH,
            "/html/body/div[2]/main/div[2]/div/div[3]/div/div/div/"
            + "div[1]/div[6]/div[2]",
        )
        ActionChains(driver).move_to_element(quatre_detail).move_by_offset(
            0, 0
        ).click().perform()
        time.sleep(5)
        driver.save_screenshot("screenshots/find_quatre_detail.png")
        self.lackey_compare(
            self.settings.quatre_detail,
            "screenshots/find_quatre_detail.png",
        )

    def workflow_banque_populaire(self):
        """Describes the general workflow
        - Start the Selenium Driver
        - Start the video record
        - Check the default browser
        - Do all the steps
        - In case of error call report and
        persist the video file
        """
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            + "AppleWebKit/537.36 (KHTML, like Gecko) "
            + "Chrome/91.0.4472.124 Safari/537.36"
        )
        if self.settings.default_browser == "edge":
            edge_service = Service(self.settings.edge_path)
            driver = webdriver.Edge(options=options, service=edge_service)
        else:
            driver = webdriver.Chrome(options=options)

        driver.maximize_window()
        video = Video(driver)
        try:
            video.start_screen_rec()

            self.step_tout_acepter(driver)
            self.step_consent_prompt_submit(driver)
            self.step_trouver_une_agence(driver)
            self.step_rue_search(driver)
            self.step_code_postal(driver)
            self.step_submit_addr(driver)
            self.step_geocoder(driver)
            self.step_quatre_detail(driver)

            video.end_screen_record()
        except Exception as err:
            logging.exception("Error: %s", err)
            driver.save_screenshot(f"screenshots/FAILED_{self.step}.png")
            video.end_screen_record(persist_video=True)
            report = Report()
            report.generate_report(video.output_filename)

        driver.quit()
