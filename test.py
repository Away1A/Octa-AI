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

# Define base directory and session folder
base_dir = os.path.join(os.getcwd(), 'static', 'screenshot')
timestamp = time.strftime('%Y%m%d%H%M%S')  # e.g., '20241121113045'
session_dir = os.path.join(base_dir, f'session_{timestamp}')
os.makedirs(session_dir, exist_ok=True)

def save_screenshot(driver, filename):
    screenshot_path = os.path.join(session_dir, f'{filename}.png')
    driver.save_screenshot(screenshot_path)

def wait_for_element(driver, by, value, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        pytest.fail(f'Element {value} not found within {timeout} seconds.')

def click_element_js(driver, element):
    driver.execute_script("arguments[0].click();", element)

@pytest.fixture
def driver():
    # Set up Chrome options
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize WebDriver with the specified service
    service = Service(executable_path='C:\\Program Files\\chromedriver-win64\\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)  # Implicit wait for elements to be found

    yield driver

    # Teardown: close the browser
    driver.quit()

def test_user_login_and_create_transaction(driver):
    # Step: Given I am on the login page
    login_url = "http://172.22.201.22:3002/login"
    driver.get(login_url)
    save_screenshot(driver, 'login_page_loaded')

    # Step: When I enters username "reza_reza" and password "Pass2323@"
    username_field = wait_for_element(driver, By.XPATH, "//input[@type='text']")
    password_field = wait_for_element(driver, By.XPATH, "//input[@type='password']")
    username_field.send_keys("reza_reza")
    password_field.send_keys("Pass2323@")
    save_screenshot(driver, 'username_and_password_filled')

    # Step: And I clicks the Log In button
    login_button = wait_for_element(driver, By.XPATH, "//button[contains(@class, 'n-button') and contains(@class, 'n-button--success-type')]")
    click_element_js(driver, login_button)
    save_screenshot(driver, 'login_button_clicked')

    # Step: Then the system displays the "Create Transaction" page
    WebDriverWait(driver, 10).until(
        EC.url_to_be("http://172.22.201.22:3002/transaction/create")
    )
    assert driver.current_url == "http://172.22.201.22:3002/transaction/create", pytest.fail('Expected "Create Transaction" page did not load.')
    save_screenshot(driver, 'create_transaction_page_loaded')

    # Step: When I am on the "Create Transaction" page
    # Step: And I leave as is on radio button with column label email CC
    # Assuming the radio button is already in the desired state, no interaction needed

    # Step: And I click "Active Directory" on radio button with column label "Requestor Source"
    requestor_source_radio = wait_for_element(driver, By.XPATH, "//div[contains(@class, 'n-radio') and contains(@class, 'n-radio--checked')]/following-sibling::div//div[contains(@class, 'n-radio')]")
    click_element_js(driver, requestor_source_radio)
    save_screenshot(driver, 'requestor_source_active_directory_selected')

    # Step: And I click the "Role" dropdown field [1]
    role_dropdown = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-base-selection') and contains(@class, 'n-base-selection-label')])[1]")
    click_element_js(driver, role_dropdown)
    save_screenshot(driver, 'role_dropdown_clicked')

    # Step: And I enter "Foreman" in the Role field
    role_input = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-base-selection')]/input)[1]")
    role_input.clear()
    role_input.send_keys("Foreman")
    role_input.send_keys(u'\ue007')  # Press ENTER
    save_screenshot(driver, 'role_filled_and_enter_pressed')

    body_element = driver.find_element(By.TAG_NAME, "body")
    body_element.click()
    save_screenshot(driver, 'role_dropdown_closed')

    # Step: When I click the "Module Name" dropdown field [2]
    module_name_dropdown = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-base-selection') and contains(@class, 'n-base-selection-label')])[2]")
    click_element_js(driver, module_name_dropdown)
    save_screenshot(driver, 'module_name_dropdown_clicked')

    # Step: And I enter "Plan Mine Closure" in the Module Name field
    module_name_input = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-base-selection')]/input)[2]")
    module_name_input.clear()
    module_name_input.send_keys("Plan Mine Closure")
    module_name_input.send_keys(u'\ue007')  # Press ENTER
    save_screenshot(driver, 'module_name_filled_and_enter_pressed')

    body_element.click()
    save_screenshot(driver, 'module_name_dropdown_closed')

    # Step: When I click the "Requestor" dropdown field [5]
    requestor_dropdown = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-base-selection') and contains(@class, 'n-base-selection-label')])[5]")
    click_element_js(driver, requestor_dropdown)
    save_screenshot(driver, 'requestor_dropdown_clicked')

    # Step: And I enter value "Atthoriq" in the Requestor field
    requestor_input = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-base-selection')]/input)[5]")
    requestor_input.clear()
    requestor_input.send_keys("Atthoriq")
    requestor_input.send_keys(u'\ue007')  # Press ENTER
    save_screenshot(driver, 'requestor_filled_and_enter_pressed')

    body_element.click()
    save_screenshot(driver, 'requestor_dropdown_closed')

    # Step: And I enter "2000" in the "Amount of Transaction" field
    amount_field = wait_for_element(driver, By.XPATH, "//input[@placeholder='Amount of Transaction']")
    amount_field.clear()
    amount_field.send_keys("2000")
    save_screenshot(driver, 'amount_filled')

    # Step: And I click the "Submit" button
    submit_button = wait_for_element(driver, By.XPATH, "//button[contains(@class, 'n-button') and contains(@class, 'n-button--success-type')]")
    click_element_js(driver, submit_button)
    save_screenshot(driver, 'submit_button_clicked')

    # Step: Then the system saves the transaction
    # Assuming there's a confirmation or a change in URL to verify successful submission
    try:
        WebDriverWait(driver, 10).until(
            EC.url_changes("http://172.22.201.22:3002/transaction/create")
        )
        save_screenshot(driver, 'transaction_saved')
    except TimeoutException:
        save_screenshot(driver, 'error_transaction_not_saved')
        pytest.fail('Transaction was not saved successfully.')

if __name__ == "__main__":
    pytest.main()