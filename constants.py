TEMPLATE_PROMPT = """
    Convert the following Gherkin scenario to a Selenium script using pytest for the URL.
    Follow these coding guidelines:
    - Use **XPath** with **multiple `contains(@class, ...)` conditions** to locate button elements with complex class attributes.
    - Use `//input[@id` or CSS Selectors for element identification.
    - For username and password fields, use XPath with `@type='text'` and `@type='password'` respectively.
    - For input fields, prefer locating by the `@placeholder` attribute for clarity and stability.
    - Use JavaScript Executor (`driver.execute_script()`) to click buttons or elements as required.
    - Make sure to use `pytest.fail()` for failures, with descriptive error messages.

    - Use the URL specified in the Gherkin scenario for `driver.get()` instead of hardcoding.
    - Make sure radio labels like the following example are handled:
    Example: 
        `requestor_source_radio = wait_for_element(driver, By.XPATH, "(//div[contains(@class, 'n-radio__label') and contains(text(), 'Active Directory')])[2]")`
    - Buttons:
    Example: 
        `login_button = wait_for_element(driver, By.XPATH, "//button[contains(@class, 'n-button') and contains(@class, 'n-button--success-type')]")`
    - For assertions, validate the current URL (`driver.current_url`) rather than the page title.

    - Dropdown selections:
        - Send the desired text to the input field and press ENTER (`u'\\ue007'`) to choose the option.
        - Use explicit waits to ensure the dropdown field contains the correct text after selection.
    - Ensure field interaction continues seamlessly to the next field once the current field is successfully filled.
    - Ensure compatibility for fields with identical XPath by using indexes or context-aware locators.
    - Add detailed logging or comments to describe each test step for better readability and maintainability.
    - For cases where the dropdown requires additional actions:
        - Wait for the dropdown to become visible using explicit waits.
        - Use JavaScript Executor to interact with complex dropdowns.
        - Ensure the dropdown closes automatically or click outside of it to force closure before proceeding.
    - No need to ensure the dropdown field is filled.
    - Follow this example for other next steps:
        Example: 
        `(//div[contains(@class, 'n-base-selection') and contains(@class, 'n-base-selection-label')])[2]`, `(//div[contains(@class, 'n-base-selection')]/input)[2]`.

    - Save screenshots for each test step with descriptive filenames that reflect the step being executed.

    Gherkin Scenario:
    {gherkin_text}

    Available Elements:
    {element_details}

    Expected Script Structure:
    - Create new driver for each test case
    - Driver Options:
        - Use headless mode in driver options for test efficiency.
        - Initialize WebDriver with the following service:
            `service = Service(executable_path='C:\\Program Files\\chromedriver-win64\\chromedriver.exe')`
    - Implicit Waits:
        - Use `WebDriverWait` for dynamic waiting of elements, especially for modals or AJAX-based elements.
    - Assertions:
        - Validate the result of each step (e.g., check URLs, content changes, or modal visibility).
    - Modal Handling:
        - Wait for modal visibility using `visibility_of_element_located`.
        - Locate elements within the modal scope using `modal.find_element` or a similar approach to avoid conflicts.
        - Ensure the modal is dismissed or closed using `invisibility_of_element` after required interactions.
    - Exception Handling:
        - Include exception handling for `TimeoutException`, `NoSuchElementException`, and `UnexpectedAlertPresentException`.
        - Take screenshots during exceptions to assist debugging.
    - Screenshots:
        - Save screenshots at key steps:
            - After page loads.
            - After performing major actions (e.g., submitting a form, interacting with a modal).
            - During exceptions or unexpected behaviors.
        - Organize screenshots into session-based subfolders:
            - Root folder: `static/screenshot`
            - Subfolder for each session: timestamp-based naming (e.g., `session_20241121113045`).
        - Use Python's `os.makedirs()` to create folders dynamically.

    Example for dynamically saving screenshots:
    ```python
    import os
    import time
    # Define base directory
    base_dir = os.path.join(os.getcwd(), 'static', 'screenshot')
    timestamp = time.strftime('%Y%m%d%H%M%S')  # e.g., '20241121113045'
    session_dir = os.path.join(base_dir, f'session_{timestamp}')
    os.makedirs(session_dir, exist_ok=True)
    # Save screenshots in the session folder
    ```
    - Code Quality:
      - Maintain consistent structure with clear variable naming and comments.
      - Include detailed error messages in assertions (e.g., `pytest.fail('Expected page did not load.')`).
"""

TEMPLATE_PROMPT_REPORT = """
    Analyze the following Selenium script and simulate its execution:

    {selenium_script}

    Identify all test cases in this script and generate a detailed test report with the following structure. 
    Ensure the output uses the exact format below for easy parsing:

    ### Test Case Identification
    1. **Test Case 1**: <Short name or title of the test case>.
    2. **Test Case 2**: <Short name or title of the test case>.
    3. **Test Case N**: <Short name or title of the test case>.

    ### Detailed Test Report
    Test Case 1
    - **Description**: <Detailed description of what this test case does>
    - **Expected Results**: <What is expected to happen during this test>
    - **Actual Results**: <Simulated results based on the Selenium script provided>
    - **Issues Found**: <List any issues identified, or state 'None'>
    - **Recommendations**: <Suggestions to fix issues or improve the script>
    - **Test Result**: <Is the test case passing or failing>

    Test Case 2
    - **Description**: <Detailed description of what this test case does>
    - **Expected Results**: <What is expected to happen during this test>
    - **Actual Results**: <Simulated results based on the Selenium script provided>
    - **Issues Found**: <List any issues identified, or state 'None'>
    - **Recommendations**: <Suggestions to fix issues or improve the script>
    - **Test Result**: <Is the test case passing or failing>

    Repeat this format for all identified test cases. 
    Ensure the report uses clear and professional language, with consistent formatting. 
    The 'Test Case Identification' section must use a numbered list, and the 'Detailed Test Report' section must 
    match the test cases listed above exactly.
"""    
    
