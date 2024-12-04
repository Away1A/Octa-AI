import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, UnexpectedAlertPresentException

# Define base directory for screenshots
base_dir = os.path.join(os.getcwd(), 'static', 'screenshot')
timestamp = time.strftime('%Y%m%d%H%M%S')  # e.g., '20241121113045'
session_dir = os.path.join(base_dir, f'session_{timestamp}')
os.makedirs(session_dir, exist_ok=True)

# Define the URL
URL = "https://www.saucedemo.com/"

# Define the service and options
service = Service(executable_path='C:\\Program Files\\chromedriver-win64\\chromedriver.exe')
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

def save_screenshot(driver, step_description):
    driver.save_screenshot(os.path.join(session_dir, f'{step_description}.png'))

@pytest.fixture
def driver():
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

def login(driver, username, password):
    driver.get(URL)
    save_screenshot(driver, 'login_page')
    try:
        username_input = driver.find_element(By.XPATH, "//input[@id='user-name']")
        password_input = driver.find_element(By.XPATH, "//input[@id='password']")
        login_button = driver.find_element(By.XPATH, "//input[@id='login-button']")
    except NoSuchElementException as e:
        save_screenshot(driver, 'login_page_exception')
        pytest.fail(f"Element not found: {e}")

    username_input.send_keys(username)
    password_input.send_keys(password)
    save_screenshot(driver, 'filled_credentials')
    driver.execute_script("arguments[0].click();", login_button)
    save_screenshot(driver, 'after_login_click')

def assert_error_message(driver, message):
    try:
        error_message = driver.find_element(By.XPATH, "//div[contains(@class, 'error-message-container')]")
        assert message in error_message.text, f"Expected error message '{message}' not found"
    except (NoSuchElementException, AssertionError) as e:
        save_screenshot(driver, 'error_message_exception')
        pytest.fail(f"Error message assertion failed: {e}")

def assert_current_url(driver, expected_url):
    assert driver.current_url == expected_url, f"Expected URL {expected_url}, but got {driver.current_url}"

def test_login_with_correct_credentials(driver):
    login(driver, "standard_user", "secret_sauce")
    assert_current_url(driver, URL + "inventory.html")

def test_login_with_correct_username_and_empty_password(driver):
    login(driver, "standard_user", "")
    assert_error_message(driver, "Password is required")
    assert_current_url(driver, URL)

def test_login_with_empty_username_and_correct_password(driver):
    login(driver, "", "secret_sauce")
    assert_error_message(driver, "Username is required")
    assert_current_url(driver, URL)

def test_login_with_empty_credentials(driver):
    login(driver, "", "")
    assert_error_message(driver, "Username is required")
    assert_current_url(driver, URL)

def test_login_with_incorrect_password(driver):
    login(driver, "standard_user", "secret")
    assert_error_message(driver, "Username and password do not match any user in this service")
    assert_current_url(driver, URL)

def test_login_with_unregistered_username(driver):
    login(driver, "standard", "secret_sauce")
    assert_error_message(driver, "Username and password do not match any user in this service")
    assert_current_url(driver, URL)