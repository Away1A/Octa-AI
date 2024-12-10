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

def take_screenshot(driver, step_description):
    driver.save_screenshot(os.path.join(session_dir, f'{step_description}.png'))

@pytest.fixture(scope='function')
def driver():
    service = Service(executable_path='C:\\Program Files\\chromedriver-win64\\chromedriver.exe')
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

def test_transaction_flow(driver):
    try:
        # Navigate to login page
        login_url = "http://172.22.201.22:3002/login"
        driver.get(login_url)
        take_screenshot(driver, 'login_page_loaded')

        # Enter username and password
        username_input = driver.find_element(By.XPATH, "//input[@type='text']")
        password_input = driver.find_element(By.XPATH, "//input[@type='password']")
        username_input.send_keys("reza_reza")
        password_input.send_keys("Pass2323@")
        take_screenshot(driver, 'credentials_entered')

        # Click Log In button
        login_button = driver.find_element(By.XPATH, "//button[contains(@class, 'n-button') and contains(@class, 'n-button--success-type')]")
        driver.execute_script("arguments[0].click();", login_button)
        take_screenshot(driver, 'login_button_clicked')

        # Wait for the transaction creation page to load
        WebDriverWait(driver, 10).until(EC.url_to_be("http://172.22.201.22:3002/transaction/create"))
        take_screenshot(driver, 'transaction_page_loaded')

        # Click the Role dropdown and enter "Foreman"
        role_dropdown = driver.find_element(By.CSS_SELECTOR, ".n-select.n-base-selection")
        role_dropdown.click()
        role_input = driver.find_element(By.XPATH, "//div[contains(@class, 'n-base-selection')]/input")
        role_input.send_keys("Foreman")
        role_option = driver.find_element(By.XPATH, "//div[contains(@class, 'n-base-selection-option') and text()='Foreman']")
        driver.execute_script("arguments[0].click();", role_option)
        take_screenshot(driver, 'role_selected')

        # Click the Module Name dropdown and enter "Plan Mine Closure"
        module_dropdown = driver.find_element(By.XPATH, "(//div[contains(@class, 'n-select') and contains(@class, 'n-base-selection')])[2]")
        driver.execute_script("arguments[0].click();", module_dropdown)
        module_input = driver.find_element(By.XPATH, "(//div[contains(@class, 'n-base-selection')]/input)[2]")
        module_input.send_keys("Plan Mine Closure")
        module_option = driver.find_element(By.XPATH, "//div[contains(@class, 'n-base-selection-option') and text()='Plan Mine Closure']")
        driver.execute_script("arguments[0].click();", module_option)
        take_screenshot(driver, 'module_selected')

        # Choose "HRIS" as the Email CC Source and Requestor Source
        email_cc_dropdown = driver.find_element(By.XPATH, "(//div[contains(@class, 'n-select') and contains(@class, 'n-base-selection')])[3]")
        driver.execute_script("arguments[0].click();", email_cc_dropdown)
        email_cc_option = driver.find_element(By.XPATH, "//div[contains(@class, 'n-base-selection-option') and text()='HRIS']")
        driver.execute_script("arguments[0].click();", email_cc_option)

        requestor_dropdown = driver.find_element(By.XPATH, "(//div[contains(@class, 'n-select') and contains(@class, 'n-base-selection')])[4]")
        driver.execute_script("arguments[0].click();", requestor_dropdown)
        requestor_option = driver.find_element(By.XPATH, "//div[contains(@class, 'n-base-selection-option') and text()='HRIS']")
        driver.execute_script("arguments[0].click();", requestor_option)
        take_screenshot(driver, 'email_cc_and_requestor_selected')

        # Enter "Atthoriq" on Requestor fields
        requestor_input = driver.find_element(By.XPATH, "(//input[@type='text'])[1]")
        requestor_input.send_keys("Atthoriq")
        take_screenshot(driver, 'requestor_entered')

        # System auto-fills Requestor Superior, Division, Location, Position, Department, and Company
        # (No action required, just verify they are filled)
        requestor_superior = driver.find_element(By.XPATH, "(//input[@type='text'])[2]")
        division = driver.find_element(By.XPATH, "(//input[@type='text'])[3]")
        location = driver.find_element(By.XPATH, "(//input[@type='text'])[4]")
        position = driver.find_element(By.XPATH, "(//input[@type='text'])[5]")
        department = driver.find_element(By.XPATH, "(//input[@type='text'])[6]")
        company = driver.find_element(By.XPATH, "(//input[@type='text'])[7]")

        assert requestor_superior.get_attribute('value'), "Requestor Superior not auto-filled"
        assert division.get_attribute('value'), "Division not auto-filled"
        assert location.get_attribute('value'), "Location not auto-filled"
        assert position.get_attribute('value'), "Position not auto-filled"
        assert department.get_attribute('value'), "Department not auto-filled"
        assert company.get_attribute('value'), "Company not auto-filled"
        take_screenshot(driver, 'auto_filled_fields_verified')

        # Enter "2000" in the "Amount of Transaction" field
        amount_input = driver.find_element(By.XPATH, "//input[@type='text'][@placeholder='Amount of Transaction']")
        amount_input.send_keys("2000")
        take_screenshot(driver, 'amount_entered')

        # Choose "Without Advanced Param" as the "Category Transaction"
        category_dropdown = driver.find_element(By.XPATH, "(//div[contains(@class, 'n-select') and contains(@class, 'n-base-selection')])[5]")
        driver.execute_script("arguments[0].click();", category_dropdown)
        category_option = driver.find_element(By.XPATH, "//div[contains(@class, 'n-base-selection-option') and text()='Without Advanced Param']")
        driver.execute_script("arguments[0].click();", category_option)
        take_screenshot(driver, 'category_selected')

        # Click the "Submit" button
        submit_button = driver.find_element(By.XPATH, "//button[contains(@class, 'n-button') and contains(@class, 'n-button--success-type') and contains(@class, 'rounded-md')]")
        driver.execute_script("arguments[0].click();", submit_button)
        take_screenshot(driver, 'submit_button_clicked')

        # Wait for the confirmation message
        confirmation_message = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'Vue-Toastification__container')]/div[contains(@class, 'Vue-Toastification__toast')]"))
        )
        assert "Submit is success with transaction number" in confirmation_message.text, "Confirmation message not displayed"
        take_screenshot(driver, 'confirmation_message_displayed')

    except TimeoutException as e:
        take_screenshot(driver, 'timeout_exception')
        pytest.fail(f"TimeoutException: {e}")
    except NoSuchElementException as e:
        take_screenshot(driver, 'no_such_element_exception')
        pytest.fail(f"NoSuchElementException: {e}")
    except UnexpectedAlertPresentException as e:
        take_screenshot(driver, 'unexpected_alert_exception')
        pytest.fail(f"UnexpectedAlertPresentException: {e}")
    except AssertionError as e:
        take_screenshot(driver, 'assertion_error')
        pytest.fail(f"AssertionError: {e}")