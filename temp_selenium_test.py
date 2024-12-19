import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, UnexpectedAlertPresentException

# Define base directory for screenshots
base_dir = os.path.join(os.getcwd(), 'static', 'screenshot')
timestamp = time.strftime('%Y%m%d%H%M%S')  # e.g., '20241121113045'
session_dir = os.path.join(base_dir, f'session_{timestamp}')
os.makedirs(session_dir, exist_ok=True)

# Define the URL
LOGIN_URL = "http://172.22.201.22:3002/login"
TRANSACTION_CREATE_URL = "http://172.22.201.22:3002/transaction/create"

# Define the service for the WebDriver
service = Service(executable_path='C:\\Program Files\\chromedriver-win64\\chromedriver.exe')

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

def take_screenshot(driver, step_description):
    driver.save_screenshot(os.path.join(session_dir, f'{step_description}.png'))

def handle_modal(driver, expected_message):
    try:
        modal = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.Vue-Toastification__toast-body'))
        )
        modal_text = modal.text
        if expected_message not in modal_text:
            pytest.fail(f'Expected modal message "{expected_message}", but got "{modal_text}".')
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element(modal)
        )
    except TimeoutException:
        pytest.fail('Modal did not appear within the expected time.')

def login(driver, username, password):
    try:
        driver.get(LOGIN_URL)
        take_screenshot(driver, 'login_page_loaded')

        # Enter username
        username_input = driver.find_element(By.XPATH, "//input[@type='text']")
        username_input.send_keys(username)

        # Enter password
        password_input = driver.find_element(By.XPATH, "//input[@type='password']")
        password_input.send_keys(password)

        # Click the Log In button
        login_button = driver.find_element(By.XPATH, "//button[contains(@class, 'n-button') and contains(@class, 'n-button--success-type')]")
        login_button.click()
        take_screenshot(driver, 'login_button_clicked')

    except (TimeoutException, NoSuchElementException, UnexpectedAlertPresentException) as e:
        take_screenshot(driver, 'login_exception')
        pytest.fail(f'An error occurred during login: {e}')

@pytest.mark.parametrize(
    "username, password, expected_url, expected_modal_message",
    [
        ("reza_reza", "Pass2323@", LOGIN_URL, None),
        ("reza_reza", "", LOGIN_URL, "Password can't be empty"),
        ("", "Pass2323@", LOGIN_URL, "Username can't be empty"),
        ("", "", LOGIN_URL, "Password can't be empty"),
        ("away", "awayaway", LOGIN_URL, "Incorrect username or password")
    ]
)
def test_login(driver, username, password, expected_url, expected_modal_message):
    login(driver, username, password)

    if expected_modal_message:
        handle_modal(driver, expected_modal_message)
        assert driver.current_url == expected_url, f'Expected URL {expected_url}, but got {driver.current_url}.'
    else:
        assert driver.current_url == expected_url, f'Expected URL {expected_url}, but got {driver.current_url}.'
    take_screenshot(driver, 'final_state')