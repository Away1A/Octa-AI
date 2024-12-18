import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, UnexpectedAlertPresentException

# Define base directory for screenshots
base_dir = os.path.join(os.getcwd(), 'static', 'screenshot')
timestamp = time.strftime('%Y%m%d%H%M%S')  # e.g., '20241121113045'
session_dir = os.path.join(base_dir, f'session_{timestamp}')
os.makedirs(session_dir, exist_ok=True)

def save_screenshot(driver, filename):
    screenshot_path = os.path.join(session_dir, f'{filename}.png')
    driver.save_screenshot(screenshot_path)
    print(f'Screenshot saved: {screenshot_path}')

def click_element_js(driver, element):
    driver.execute_script("arguments[0].click();", element)

def wait_for_element(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except TimeoutException:
        pytest.fail(f'Element not found: {value}')

def wait_for_element_to_be_clickable(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))
    except TimeoutException:
        pytest.fail(f'Element not clickable: {value}')

def wait_for_text_to_be_present_in_element(driver, element, text, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(EC.text_to_be_present_in_element((By.XPATH, element), text))
    except TimeoutException:
        pytest.fail(f'Text not present in element: {text}')

@pytest.fixture(scope="function")
def driver():
    service = Service(executable_path='C:\\Program Files\\chromedriver-win64\\chromedriver.exe')
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

def test_transaction_complete(driver):
    # Step: Open Login Page
    login_url = "http://172.22.201.22:3002"
    driver.get(login_url)
    save_screenshot(driver, 'login_page_loaded')

    # Step: Enter Username and Password
    username_field = wait_for_element(driver, By.XPATH, "//input[@type='text']")
    password_field = wait_for_element(driver, By.XPATH, "//input[@type='password']")
    username_field.send_keys("reza_reza")
    password_field.send_keys("Pass2323@")
    save_screenshot(driver, 'username_password_filled')

    # Step: Click Log In Button
    login_button = wait_for_element(driver, By.XPATH, "//button[contains(@class, 'n-button') and contains(@class, 'n-button--success-type')]")
    click_element_js(driver, login_button)
    save_screenshot(driver, 'login_button_clicked')

    # Step: Validate Redirect to Create Transaction Page
    WebDriverWait(driver, 10).until(EC.url_to_be("http://172.22.201.22:3002/transaction/create"))
    save_screenshot(driver, 'create_transaction_page_loaded')
    assert driver.current_url == "http://172.22.201.22:3002/transaction/create", "Failed to navigate to Create Transaction page"

    # Step: Click "Active Directory" on radio button with column label "Requestor Source" [2]
    requestor_source_radio = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-radio__label') and contains(text(), 'Active Directory')])[2]")
    click_element_js(driver, requestor_source_radio)
    save_screenshot(driver, 'requestor_source_radio_clicked')

    # Step: Click "Role" dropdown field [1]
    role_dropdown = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-base-selection') and contains(@class, 'n-base-selection-label')])[1]")
    click_element_js(driver, role_dropdown)
    save_screenshot(driver, 'role_dropdown_clicked')

    # Step: Enter "Foreman" in the Role field
    role_input = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-base-selection')]/input)[1]")
    role_input.clear()
    role_input.send_keys("Foreman")
    role_input.send_keys(Keys.ENTER)
    save_screenshot(driver, 'role_filled_and_enter_pressed')

    body_element = driver.find_element(By.TAG_NAME, "body")
    body_element.click()
    save_screenshot(driver, 'role_dropdown_closed')

    # Step: Click "Module Name" dropdown field [2]
    module_dropdown = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-base-selection') and contains(@class, 'n-base-selection-label')])[2]")
    click_element_js(driver, module_dropdown)
    save_screenshot(driver, 'module_dropdown_clicked')

    # Step: Enter "Plan Mine Closure" in the Module Name field
    module_input = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-base-selection')]/input)[2]")
    module_input.clear()
    module_input.send_keys("Plan Mine Closure")
    module_input.send_keys(Keys.ENTER)
    save_screenshot(driver, 'module_filled_and_enter_pressed')

    body_element.click()
    save_screenshot(driver, 'module_dropdown_closed')

    # Step: Click "Requestor" dropdown field [5]
    requestor_dropdown = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-base-selection') and contains(@class, 'n-base-selection-label')])[5]")
    click_element_js(driver, requestor_dropdown)
    save_screenshot(driver, 'requestor_dropdown_clicked')

    # Step: Enter value "Atthoriq" in the Requestor field
    requestor_input = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-base-selection')]/input)[5]")
    requestor_input.clear()
    requestor_input.send_keys("Atthoriq")
    requestor_input.send_keys(Keys.ENTER)
    save_screenshot(driver, 'requestor_filled_and_enter_pressed')

    body_element.click()
    save_screenshot(driver, 'requestor_dropdown_closed')

    # Step: Click "Active Directory" on radio button with column label "Requestor Superior Source" [3]
    requestor_superior_radio = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-radio__label') and contains(text(), 'Active Directory')])[3]")
    click_element_js(driver, requestor_superior_radio)
    save_screenshot(driver, 'requestor_superior_radio_clicked')

    # Step: Click "Requestor Superior" dropdown field [6]
    requestor_superior_dropdown = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-base-selection') and contains(@class, 'n-base-selection-label')])[6]")
    click_element_js(driver, requestor_superior_dropdown)
    save_screenshot(driver, 'requestor_superior_dropdown_clicked')

    # Step: Enter value "Reza" in the Requestor Superior field
    requestor_superior_input = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-base-selection')]/input)[6]")
    requestor_superior_input.clear()
    requestor_superior_input.send_keys("Reza")
    requestor_superior_input.send_keys(Keys.ENTER)
    save_screenshot(driver, 'requestor_superior_filled_and_enter_pressed')

    body_element.click()
    save_screenshot(driver, 'requestor_superior_dropdown_closed')

    # Step: Enter "2000" in the "Amount of Transaction" field
    amount_field = wait_for_element(driver, By.XPATH, "//input[@placeholder='Amount of Transaction']")
    amount_field.clear()
    amount_field.send_keys("2000")
    save_screenshot(driver, 'amount_filled')

    # Step: Click the "Submit" button
    submit_button = wait_for_element(driver, By.XPATH, "//button[contains(@class, 'n-button') and contains(@class, 'n-button--success-type')]")
    click_element_js(driver, submit_button)
    save_screenshot(driver, 'submit_button_clicked')

    # Step: Validate the system saves the transaction and user navigates to document page
    WebDriverWait(driver, 10).until(EC.url_to_be("http://172.22.201.22:3002/document/all"))
    save_screenshot(driver, 'document_page_loaded')
    assert driver.current_url == "http://172.22.201.22:3002/document/all", "Failed to navigate to Document page"
    

def test_requestor_source_empty_while_requestor_filled(driver):
    # Step: Open Login Page
    login_url = "http://172.22.201.22:3002"
    driver.get(login_url)
    save_screenshot(driver, 'login_page_loaded')

    # Step: Enter Username and Password
    username_field = wait_for_element(driver, By.XPATH, "//input[@type='text']")
    password_field = wait_for_element(driver, By.XPATH, "//input[@type='password']")
    username_field.send_keys("reza_reza")
    password_field.send_keys("Pass2323@")
    save_screenshot(driver, 'username_password_filled')

    # Step: Click Log In Button
    login_button = wait_for_element(driver, By.XPATH, "//button[contains(@class, 'n-button') and contains(@class, 'n-button--success-type')]")
    click_element_js(driver, login_button)
    save_screenshot(driver, 'login_button_clicked')

    # Step: Validate Redirect to Create Transaction Page
    WebDriverWait(driver, 10).until(EC.url_to_be("http://172.22.201.22:3002/transaction/create"))
    save_screenshot(driver, 'create_transaction_page_loaded')
    assert driver.current_url == "http://172.22.201.22:3002/transaction/create", "Failed to navigate to Create Transaction page"

    # Step: Click "Active Directory" on radio button with column label "Requestor Source" [2]
    requestor_source_radio = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-radio__label') and contains(text(), 'Active Directory')])[2]")
    click_element_js(driver, requestor_source_radio)
    save_screenshot(driver, 'requestor_source_radio_clicked')

    # Step: Click "Role" dropdown field [1]
    role_dropdown = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-base-selection') and contains(@class, 'n-base-selection-label')])[1]")
    click_element_js(driver, role_dropdown)
    save_screenshot(driver, 'role_dropdown_clicked')

    # Step: Enter "Foreman" in the Role field
    role_input = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-base-selection')]/input)[1]")
    role_input.clear()
    role_input.send_keys("Foreman")
    role_input.send_keys(Keys.ENTER)
    save_screenshot(driver, 'role_filled_and_enter_pressed')

    body_element = driver.find_element(By.TAG_NAME, "body")
    body_element.click()
    save_screenshot(driver, 'role_dropdown_closed')

    # Step: Click "Module Name" dropdown field [2]
    module_dropdown = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-base-selection') and contains(@class, 'n-base-selection-label')])[2]")
    click_element_js(driver, module_dropdown)
    save_screenshot(driver, 'module_dropdown_clicked')

    # Step: Enter "Plan Mine Closure" in the Module Name field
    module_input = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-base-selection')]/input)[2]")
    module_input.clear()
    module_input.send_keys("Plan Mine Closure")
    module_input.send_keys(Keys.ENTER)
    save_screenshot(driver, 'module_filled_and_enter_pressed')

    body_element.click()
    save_screenshot(driver, 'module_dropdown_closed')

    # Step: Click "Requestor" dropdown field [5]
    requestor_dropdown = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-base-selection') and contains(@class, 'n-base-selection-label')])[5]")
    click_element_js(driver, requestor_dropdown)
    save_screenshot(driver, 'requestor_dropdown_clicked')

    # Step: Enter value "Atthoriq" in the Requestor field
    requestor_input = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-base-selection')]/input)[5]")
    requestor_input.clear()
    requestor_input.send_keys("Atthoriq")
    requestor_input.send_keys(Keys.ENTER)
    save_screenshot(driver, 'requestor_filled_and_enter_pressed')

    body_element.click()
    save_screenshot(driver, 'requestor_dropdown_closed')

    # Step: Click "Active Directory" on radio button with column label "Requestor Superior Source" [3]
    requestor_superior_radio = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-radio__label') and contains(text(), 'Active Directory')])[3]")
    click_element_js(driver, requestor_superior_radio)
    save_screenshot(driver, 'requestor_superior_radio_clicked')

    # Step: Enter "2000" in the "Amount of Transaction" field
    amount_field = wait_for_element(driver, By.XPATH, "//input[@placeholder='Amount of Transaction']")
    amount_field.clear()
    amount_field.send_keys("2000")
    save_screenshot(driver, 'amount_filled')

    # Step: Click the "Submit" button
    submit_button = wait_for_element(driver, By.XPATH, "//button[contains(@class, 'n-button') and contains(@class, 'n-button--success-type')]")
    click_element_js(driver, submit_button)
    save_screenshot(driver, 'submit_button_clicked')

    # Step: Validate URL does not change
    current_url = driver.current_url
    assert current_url == "http://172.22.201.22:3002/transaction/create", \
        f"Unexpected navigation. Current URL: {current_url}"
    save_screenshot(driver, 'validation_failed_url_not_changed')