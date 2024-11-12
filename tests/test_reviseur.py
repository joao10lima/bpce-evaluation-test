import os
import sys
from unittest import mock
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from selenium.webdriver.common.by import By

from reviseur.reviewer import Reviseur


@pytest.fixture
def mock_settings():
    settings = mock.MagicMock()
    settings.tout_accepter = "expected_tout_accepter.png"
    settings.trouver_une_agence = "expected_trouver_une_agence.png"
    settings.rue_type = "expected_rue_type.png"
    settings.code_postal = "expected_code_postal.png"
    settings.rechercher_click = "expected_rechercher_click.png"
    settings.cinq_agences_banque = "expected_cinq_agences_banque.png"
    settings.quatre_detail = "expected_quatre_detail.png"
    settings.default_browser = "chrome"
    return settings


@pytest.fixture
def reviseur(mock_settings):
    return Reviseur(mock_settings)


def test_click_element(reviseur):
    mock_element = MagicMock()
    reviseur.click_element(mock_element)
    mock_element.click.assert_called_once()


@patch("reviseur.reviewer.cv2.matchTemplate")
@patch("reviseur.reviewer.cv2.resize")
@patch("reviseur.reviewer.cv2.imread")
def test_lackey_compare_successful_match(
    mock_imread, mock_resize, mock_matchTemplate, reviseur
):
    mock_imread.side_effect = [np.zeros((500, 500)), np.zeros((500, 500))]
    match_result = np.array([[0.95]])
    mock_matchTemplate.return_value = match_result
    revis = reviseur
    revis.step = "3_trouver_une_agence"

    try:
        revis.lackey_compare(
            "path/to/expected.png", "path/to/actual.png", threshold=0.9
        )
    except Exception:
        pytest.fail("Unexpected exception raised!")


@patch("reviseur.reviewer.cv2.matchTemplate")
@patch("reviseur.reviewer.cv2.resize")
@patch("reviseur.reviewer.cv2.imread")
def test_lackey_compare_mismatch_raises_exception(
    mock_imread, mock_resize, mock_matchTemplate, reviseur
):
    mock_imread.side_effect = [np.zeros((500, 500)), np.zeros((500, 500))]
    match_result = np.array([[100] for _ in range(0, 101)])
    mock_matchTemplate.return_value = match_result
    revis = reviseur
    revis.step = "3_trouver_une_agence"
    with pytest.raises(Exception, match="Inconsistency"):
        revis.lackey_compare(
            "path/to/expected.png", "path/to/actual.png", threshold=0.9
        )


@mock.patch("reviseur.reviewer.Reviseur.lackey_compare")
def test_step_tout_accepter(mock_lackey_compare, reviseur):
    driver = MagicMock()
    reviseur.step_tout_acepter(driver)
    driver.get.assert_called_once_with("https://www.banquepopulaire.fr")
    driver.save_screenshot.assert_called_once_with(
        "screenshots/tout_acepter_before_click.png"
    )
    mock_lackey_compare.assert_called_once_with(
        reviseur.settings.tout_accepter,
        "screenshots/tout_acepter_before_click.png",
    )


@patch("reviseur.reviewer.Reviseur.lackey_compare")
@patch("reviseur.reviewer.Reviseur.click_element")
@patch("reviseur.reviewer.ActionChains")
@patch("selenium.webdriver.Chrome")
def test_step_trouver_une_agence(
    mock_webdriver, mock_action_chains, mock_click_element, mock_lackey_compare
):
    settings = MagicMock()
    reviseur = Reviseur(settings)
    driver = mock_webdriver()

    agence_element = MagicMock()
    driver.find_element.return_value = agence_element
    action_chain_instance = mock_action_chains.return_value
    driver.save_screenshot = MagicMock()

    reviseur.step_trouver_une_agence(driver)

    driver.find_element.assert_called_once_with(
        By.XPATH,
        "//p[@class='font-text-body-bold']"
        + "[normalize-space()='Trouver une agence']",
    )
    action_chain_instance.move_to_element.assert_called_once_with(
        agence_element
    )
    driver.execute_script.assert_called_once_with("window.scrollBy(0, 1000);")
    driver.save_screenshot.assert_called_once_with(
        "screenshots/trouver_une_agence_click.png"
    )
    mock_lackey_compare.assert_called_once_with(
        reviseur.settings.trouver_une_agence,
        "screenshots/trouver_une_agence_click.png",
    )
    mock_click_element.assert_called_once_with(agence_element)
