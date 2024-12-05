from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

def setup_driver():
    service = ChromeService(executable_path='C:\Program Files\chromedriver-win64\chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def wait_for_element(driver, by, value):
    try:
        return WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, value)))
    except Exception as e:
        print(f"Element not found: {e}")
        take_screenshot(driver, "element_not_found")
        pytest.fail("Expected element did not load.")

def take_screenshot(driver, description):
    base_dir = os.path.join(os.getcwd(), 'static', 'screenshot')
    timestamp = time.strftime('%Y%m%d%H%M%S')  # e.g., '20241121113045'
    session_dir = os.path.join(base_dir, f'session_{timestamp}')
    os.makedirs(session_dir, exist_ok=True)

    filename = f"{description}_{timestamp}.png"
    driver.save_screenshot(os.path.join(session_dir, filename))

def test_add_to_cart_and_checkout():
    driver = setup_driver()
    try:
        # Navigate to the home page
        driver.get("http://yourwebsite.com")
        take_screenshot(driver, "home_page_load")

        # Wait for and click on an item to add it to cart
        product_element = wait_for_element(driver, By.XPATH, "//div[@id='product-1']")
        if product_element:
            product_element.click()

        # Add to cart button
        add_to_cart_button = wait_for_element(driver, By.CSS_SELECTOR, ".add-to-cart-button")
        if add_to_cart_button:
            add_to_cart_button.click()
            take_screenshot(driver, "item_added_to_cart")

        # Proceed to checkout
        proceed_checkout_button = wait_for_element(driver, By.XPATH, "//button[text()='Proceed to Checkout']")
        if proceed_checkout_button:
            proceed_checkout_button.click()

        # Wait for and complete the checkout process
        form_input_fields = driver.find_elements(By.CSS_SELECTOR, ".form-control")
        for field in form_input_fields:
            field.send_keys("test value")  # Replace with actual test data

        # Submit button
        submit_button = wait_for_element(driver, By.XPATH, "//button[text()='Submit']")
        if submit_button:
            submit_button.click()
            take_screenshot(driver, "checkout_complete")

    except Exception as e:
        print(f"An error occurred: {e}")
        take_screenshot(driver, "unexpected_error")
        pytest.fail("Unexpected exception during test execution.")

    finally:
        driver.quit()

if __name__ == "__main__":
    import pytest
    test_add_to_cart_and_checkout()