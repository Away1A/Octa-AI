import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, UnexpectedAlertPresentException
import pytest

# Define base directory for screenshots
base_dir = os.path.join(os.getcwd(), 'static', 'screenshot')
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
session_dir = os.path.join(base_dir, f'session_{timestamp}')
os.makedirs(session_dir, exist_ok=True)

def save_screenshot(driver, filename):
    screenshot_path = os.path.join(session_dir, f'{filename}.png')
    driver.save_screenshot(screenshot_path)
    print(f'Screenshot saved: {screenshot_path}')

def click_element_js(driver, element):
    driver.execute_script("arguments[0].click();", element)
    
def wait_for_clickable(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))

def wait_for_element(driver, by, locator, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, locator)))
    except TimeoutException:
        save_screenshot(driver, f'element_timeout_{locator}')
        pytest.fail(f'Element {locator} not found within {timeout} seconds')

def wait_for_element_visible(driver, by, locator, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, locator)))
    except TimeoutException:
        save_screenshot(driver, f'element_visible_timeout_{locator}')
        pytest.fail(f'Element {locator} not visible within {timeout} seconds')

def fill_dropdown(driver, dropdown_xpath, input_xpath, value):
    try:
        dropdown = wait_for_element(driver, By.XPATH, dropdown_xpath)
        click_element_js(driver, dropdown)
        save_screenshot(driver, f'dropdown_{value}_clicked')

        input_field = wait_for_element(driver, By.XPATH, input_xpath)
        input_field.clear()
        input_field.send_keys(value)
        input_field.send_keys(Keys.ENTER)
        save_screenshot(driver, f'{value}_entered_and_enter_pressed')

        # Wait for the dropdown to be populated with the selected value
        wait_for_element_visible(driver, By.XPATH, f"{input_xpath}[contains(@value, '{value}')]")
        save_screenshot(driver, f'{value}_dropdown_populated')

        # Click outside to close the dropdown
        body_element = driver.find_element(By.TAG_NAME, "body")
        body_element.click()
        save_screenshot(driver, f'dropdown_{value}_closed')
    except Exception as e:
        save_screenshot(driver, f'dropdown_{value}_fill_failure')
        pytest.fail(f'Failed to fill dropdown with {value}: {str(e)}')

def test_user_login_and_create_transaction():
    service = Service(executable_path='C:\\Program Files\\chromedriver-win64\\chromedriver.exe')
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(5)

    try:
        # Step 1: Navigate to the login page
        driver.get('http://172.22.201.22:3002/login')
        save_screenshot(driver, 'login_page_loaded')

        # Step 2: Enter username and password
        username_field = wait_for_element(driver, By.XPATH, "//input[@type='text']")
        username_field.send_keys("reza_reza")
        save_screenshot(driver, 'username_entered')

        password_field = wait_for_element(driver, By.XPATH, "//input[@type='password']")
        password_field.send_keys("Pass2323@")
        save_screenshot(driver, 'password_entered')

        # Step 3: Click the Log In button
        login_button = wait_for_clickable(driver, By.XPATH, "//button[contains(@class, 'n-button') and contains(@class, 'n-button--success-type')]")
        click_element_js(driver, login_button)
        save_screenshot(driver, 'login_button_clicked')

        # Step 4: Verify redirected to Create Transaction page
        WebDriverWait(driver, 10).until(EC.url_to_be('http://172.22.201.22:3002/transaction/create'))
        save_screenshot(driver, 'create_transaction_page_loaded')

        # Step 5: Enter Role
        fill_dropdown(driver, "//div[contains(@class, 'n-base-selection') and contains(@class, 'n-base-selection-label')]", "//div[contains(@class, 'n-base-selection')]/input", "Foreman")

        # Step 6: Enter Module Name
        fill_dropdown(driver, "(//div[contains(@class, 'n-base-selection') and contains(@class, 'n-base-selection-label')])[2]", "(//div[contains(@class, 'n-base-selection')]/input)[2]", "Plan Mine Closure")

        # Step 7: Enter Cluster Name
        fill_dropdown(driver, "(//div[contains(@class, 'n-base-selection') and contains(@class, 'n-base-selection-label')])[3]", "(//div[contains(@class, 'n-base-selection')]/input)[3]", "Test Cluster 2")

        # Step 8: Select Email CC Source
        email_cc_source_dropdown = wait_for_element(driver, By.XPATH, "//div[contains(@class, 'n-select') and contains(@class, 'n-select--placeholder')]")
        click_element_js(driver, email_cc_source_dropdown)
        save_screenshot(driver, 'email_cc_source_dropdown_clicked')

        email_cc_source_input = wait_for_element(driver, By.XPATH, "//div[contains(@class, 'n-select')]/input")
        email_cc_source_input.clear()
        email_cc_source_input.send_keys("HRIS")
        email_cc_source_input.send_keys(Keys.ENTER)
        save_screenshot(driver, 'hris_selected_as_email_cc_source')

        # Step 9: Enter Email CC
        fill_dropdown(driver, "(//div[contains(@class, 'n-base-selection') and contains(@class, 'n-base-selection-label')])[4]", "(//div[contains(@class, 'n-base-selection')]/input)[4]", "Atthoriq")

        # Step 10: Select Requestor Source
        requestor_source_dropdown = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-select') and contains(@class, 'n-select--placeholder')])[2]")
        click_element_js(driver, requestor_source_dropdown)
        save_screenshot(driver, 'requestor_source_dropdown_clicked')

        requestor_source_input = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-select')]/input)[2]")
        requestor_source_input.clear()
        requestor_source_input.send_keys("HRIS")
        requestor_source_input.send_keys(Keys.ENTER)
        save_screenshot(driver, 'hris_selected_as_requestor_source')

        # Step 11: Enter Requestor
        requestor_field = wait_for_element(driver, By.XPATH, "//input[@placeholder='Requestor']")
        requestor_field.send_keys("Atthoriq")
        save_screenshot(driver, 'requestor_entered')

        # Wait for auto-fill to complete
        WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element((By.XPATH, "//input[@placeholder='Requestor Superior']"), "Atthoriq"))
        save_screenshot(driver, 'requestor_superior_filled')

        # Step 12: Enter Amount of Transaction
        amount_field = wait_for_element(driver, By.XPATH, "//input[@placeholder='Amount of Transaction']")
        amount_field.send_keys("2000")
        save_screenshot(driver, 'amount_of_transaction_entered')

        # Step 13: Choose Category Transaction
        category_transaction_dropdown = wait_for_element(driver, By.XPATH, "//div[contains(@class, 'n-select') and contains(@class, 'n-select--placeholder') and contains(@placeholder, 'Category Transaction')]")
        click_element_js(driver, category_transaction_dropdown)
        save_screenshot(driver, 'category_transaction_dropdown_clicked')

        category_transaction_input = wait_for_element(driver, By.XPATH, "//div[contains(@class, 'n-select')]/input")
        category_transaction_input.clear()
        category_transaction_input.send_keys("Without Advanced Param")
        category_transaction_input.send_keys(Keys.ENTER)
        save_screenshot(driver, 'without_advanced_param_selected')

        # Step 14: Click Submit button
        submit_button = wait_for_element(driver, By.XPATH, "//button[contains(@class, 'n-button__content') and contains(@class, 'n-button--success-type')]")
        click_element_js(driver, submit_button)
        save_screenshot(driver, 'submit_button_clicked')

        # Step 15: Verify transaction is saved and confirmation message is displayed
        WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element((By.XPATH, "//div[contains(@class, 'Vue-Toastification__toast--success')]"), "Submit is success with transaction number"))
        save_screenshot(driver, 'transaction_saved')

    except (TimeoutException, NoSuchElementException, UnexpectedAlertPresentException) as e:
        save_screenshot(driver, 'exception_occurred')
        pytest.fail(f'An exception occurred: {str(e)}')
    finally:
        driver.quit()