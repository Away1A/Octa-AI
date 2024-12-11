TEMPLATE_PROMPT = """
Convert the following Gherkin scenario to a Selenium script using pytest for the URL.
Follow these coding guidelines:
- Use **XPath** with **multiple `contains(@class, ...)` conditions** to locate button elements with complex class attributes.
- Use `//input[@id` or CSS Selectors for element identification.
- For password and username use xpath with correct type 
- Use XPath with attributes (if available) or CSS Selector. 
- Use JavaScript Executor to click buttons or elements as required.
- Ensure modal pop-ups or overlays are handled correctly by scoping actions within the modal context.
- Make sure to use `pytest.fail()` for failures, with descriptive error messages.

- Use the URL specified in the Gherkin scenario for `driver.get()` instead of hardcoding.
- For assertions, validate the current URL (`driver.current_url`) rather than the driver title.

Gherkin Scenario:
{gherkin_text}

Available Elements:
{element_details}

Expected Script Structure:
- Create new driver for each test case
- Driver Options:
  - Use headless mode in driver options for test efficiency.
  - Initialize WebDriver with the following service:
    `service = Service(executable_path = 'C:\\Program Files\\chromedriver-win64\\chromedriver.exe')`
- Implicit Waits:
  - Use `WebDriverWait` for dynamic waiting of elements, especially for modals or AJAX-based elements.
- Assertions:
  - Validate the result of each step (e.g., check URLs, content changes, or modal visibility).
- Modal Handling:
  - Wait for modal visibility using `visibility_of_element_located`.
  - Locate elements within the modal scope using `modal.find_element` or a similar approach to avoid conflicts.
  - Ensure modal is dismissed or closed using `invisibility_of_element` after required interactions.
- Exception Handling:
  - Include exception handling for `TimeoutException`, `NoSuchElementException`, and `UnexpectedAlertPresentException`.
  - Take screenshots during exceptions to assist debugging.
- Screenshots:
  - Save screenshots at key steps:
    - After page loads.
    - After performing major actions (e.g., submitting a form, interacting with all modal).
    - During exceptions or unexpected behaviors.
  - Organize screenshots into session-based subfolders:
    - Root folder: `static/screenshot`
    - Subfolder for each session: timestamp-based naming (e.g., `session_20241121113045`).
  - Use Python's `os.makedirs()` to create folders dynamically.
- Example for dynamically saving screenshots:
  ```python
  import os
  import time
  # Define base directory
  base_dir = os.path.join(os.getcwd(), 'static', 'screenshot')
  timestamp = time.strftime('%Y%m%d%H%M%S')  # e.g., '20241121113045'
  session_dir = os.path.join(base_dir, f'session_{timestamp}')
  os.makedirs(session_dir, exist_ok=True)
  # Save screenshots in the session folder
  driver.save_screenshot(os.path.join(session_dir, 'step_description.png'))
  ```
- Code Quality:
  - Maintain consistent structure with clear variable naming and comments.
  - Include detailed error messages in assertions (e.g., `pytest.fail('Expected page did not load.')`).
"""

TEMPLATE_PROMPT_REPORT = """
    Analyze the following Selenium script and simulate its execution:
    {selenium_script}
    Identify all test cases in this script and generate a detailed test report with the following structure:
    - **Test Case**: Name and description of the test case.
    - **Expected Results**: Describe what the test case is intended to validate.
    - **Actual Results**: Simulate the execution and provide a summary of the outcomes.
    - **Issues Found**: Highlight any issues encountered during the test.
    - **Recommendations**: Suggest fixes or improvements for the script.
    Generate the report in a professional tone and also list the test cases identified in the script.
"""
        
    
