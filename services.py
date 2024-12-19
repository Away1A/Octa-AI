import json
import subprocess
from constants import TEMPLATE_PROMPT, TEMPLATE_PROMPT_REPORT
from huggingface_hub import InferenceClient
import os
import re
import logging
from model import TestHistory, SeleniumScript, WebElementData
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from flask_socketio import SocketIO, emit
from sqlalchemy import func
from fpdf import FPDF
from pathlib import Path
import os
import datetime

session_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
screenshot_folder = os.path.join("static", "screenshot", f'session_{session_timestamp}')
client = InferenceClient("Qwen/Qwen2.5-Coder-32B-Instruct", token="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")

def get_latest_session_folder(base_folder):
    """Mendapatkan folder dengan timestamp terbaru di dalam base_folder."""
    try:
        # Dapatkan semua folder dalam base folder
        session_folders = [
            os.path.join(base_folder, d)
            for d in os.listdir(base_folder)
            if os.path.isdir(os.path.join(base_folder, d)) and d.startswith("session_")
        ]

        # Urutkan folder berdasarkan waktu terakhir dimodifikasi (atau nama folder timestamp)
        session_folders.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        # Return folder terbaru (jika ada)
        if session_folders:
            return session_folders[0]
        else:
            return None
    except Exception as e:
        logging.error(f"Error finding latest session folder: {e}")
        return None
    
def read_gherkin_file(file_path):
    try:
        with open(file_path, "r") as file:
            content = file.read()
        logging.debug(f"File {file_path} read successfully.")
        return content
    except Exception as e:
        logging.error(f"Failed to read file {file_path}: {e}")

def get_element_xpath(element):
    """
    Generate the XPath for a given WebElement.
    """
    components = []
    while element.tag_name != 'html':
        siblings = element.find_elements(By.XPATH, f"preceding-sibling::{element.tag_name}")
        siblings_count = len(siblings) + 1
        components.append(f"{element.tag_name}[{siblings_count}]")
        element = element.find_element(By.XPATH, "..")  # move up to the parent node
    components.reverse()
    return '/' + '/'.join(components)

def scrape_elements(login_url, target_url, db_session):
    try:
        # Konfigurasi Chrome Options
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Inisialisasi Service dan WebDriver
        service = Service(executable_path='C:\\Program Files\\chromedriver-win64\\chromedriver.exe')
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Buka halaman login dan tunggu login manual
        driver.get(login_url)
        logging.info("Silakan login secara manual. Tunggu hingga login selesai.")

        # Tunggu sampai URL halaman target tercapai setelah login
        WebDriverWait(driver, 300).until(lambda d: d.current_url == target_url)
        logging.info(f"Login selesai. Halaman saat ini: {driver.current_url}")

        # Pastikan halaman yang dibuka adalah halaman target
        if driver.current_url != target_url:
            logging.warning(f"Gagal mencapai halaman target. Halaman saat ini: {driver.current_url}")
            return

        # Tunggu sampai halaman sepenuhnya dimuat sebelum scraping
        logging.info("Menunggu halaman sepenuhnya dimuat...")
        WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located((By.XPATH, '//div | //section | //form')))

        # Temukan semua container di halaman (div, section, atau form)
        containers = driver.find_elements(By.XPATH, '//div | //section | //form')
        if not containers:
            logging.warning("Tidak ada container ditemukan di halaman target.")
            return

        logging.info(f"Ditemukan {len(containers)} container di halaman. Memulai scraping...")

        for container in containers:
            try:
                # Cari elemen-elemen dalam setiap container
                elements = container.find_elements(By.XPATH, './/*')
                if not elements:
                    continue

                for element in elements:
                    try:
                        xpath = get_element_xpath(element)
                        attribute = element.get_attribute("class") or element.get_attribute("id") or "No attribute"
                        text_content = element.text

                        # Buat instance WebElementData dan tambahkan ke sesi database
                        web_element_data = WebElementData(
                            url=target_url,
                            xpath=xpath,
                            attribute=attribute,
                            text_content=text_content
                        )
                        db_session.add(web_element_data)
                    except Exception as e:
                        logging.error(f"Gagal memproses elemen dalam container: {e}")
            except Exception as e:
                logging.error(f"Gagal memproses container: {e}")

        # Simpan semua data elemen yang ditemukan ke database
        db_session.commit()
        logging.info(f"Berhasil melakukan scraping semua container dari {target_url}.")

    except Exception as e:
        logging.error(f"Gagal melakukan scraping dari {target_url}: {e}")

    finally:
        # Pastikan driver selalu ditutup meskipun terjadi kesalahan
        driver.quit()
        logging.info("Driver ditutup.")

def generate_selenium_script(gherkin_text, login_url, target_url, use_template=False):

    # Ambil domain dari login_url
    domain = "/".join(login_url.split("/")[:3])  
    
    # Query semua elemen kecuali yang memiliki attribute 'No Attribute'
    elements = WebElementData.query.filter(
        WebElementData.url.like(f"{domain}%"),  # Hanya elemen di domain yang sama
        WebElementData.attribute != "No Attribute"  # Exclude elemen dengan attribute 'No Attribute'
    ).all()

    # Logging hasil query
    logging.info(f"Total elements retrieved: {len(elements)}")
    for el in elements:
        logging.info(f"Retrieved element - URL: {el.url}, Attribute: '{el.attribute}', Text: '{el.text_content}', XPath: {el.xpath}")

    # Gabungkan detail elemen
    element_details = "\n".join(set(el.attribute for el in elements))
    logging.info(f"Total elements retrieved: {len(element_details)}")

    # Buat template prompt
    template_prompt = TEMPLATE_PROMPT.format(
        gherkin_text=gherkin_text,
        element_details=element_details
    )

    if use_template:
        example_script = SeleniumScript.query.filter_by(status="passed").first()
        if example_script:
            template_prompt += f"\n\ngive log for every step and Example script:\n\n{example_script.script_content}"
            logging.debug("Template prompt with example script found and added.")

    messages = [{"role": "user", "content": template_prompt}]
    response = ""
    try:
        for message in client.chat_completion(messages, max_tokens=3000, stream=True, temperature=0.7, top_p=0.95):
            response += message.choices[0].delta.content
        logging.info("Selenium script generated successfully.")
    except Exception as e:
        logging.critical(f"Failed to generate script from model: {e}")
    return response.strip()

def clean_code_with_regex(text):
    match = re.search(r"```(python|py)(.*?)```", text, re.DOTALL)
    if match:
        code = match.group(2).strip()
        logging.debug("Code cleaned with regex.")
        return code
    logging.warning("No code block found to clean.")
    return ""

def run_pytest(file_name):
    try:
        # Menjalankan pytest dengan opsi laporan JSON
        result = subprocess.run(
            ["pytest", file_name, "--json-report"],
            capture_output=True, text=True
        )
        logging.info("Pytest executed successfully.")

        # Membaca output JSON dari file laporan
        report_path = ".report.json"  # Path default laporan JSON

        if result.returncode == 0:
            # Jika pytest sukses, membaca hasil laporan
            with open(report_path, "r") as f:
                report_data = json.load(f)
                return report_data
        else:
            logging.error(f"Pytest failed with return code {result.returncode}.")
            with open(report_path, "r") as f:
                report_data = json.load(f)
                return report_data
    except Exception as e:
        logging.error(f"Failed to run pytest on {file_name}: {e}")
        return None

def calculate_lines(content, width, font_size):
    # Get the width of the content (approximate)
    line_height = font_size * 0.8  # Approximate line height (adjust as necessary)
    max_width = width - 4  # Subtract padding
    num_lines = (len(content) * font_size) / max_width
    return max(1, int(num_lines))

def generate_test_report(selenium_script, report_name, report_data, use_template=False):
    """
    Generate a test report using AI, run pytest to test the script, and save as a PDF.
    
    Args:
        selenium_script (str): Content of the Selenium script.
        report_name (str): Name of the report file (without extension).
        use_template (bool): Whether to use a template for report generation.
    
    Returns:
        str: Path to the generated PDF report.
    """

    # Validasi parameter
    if not selenium_script.strip():
        raise ValueError("Selenium script cannot be empty.")
    if not report_name.strip():
        raise ValueError("Report name cannot be empty.")

    # Langkah 1: Menganalisis script untuk menemukan test case menggunakan AI
    test_cases, ai_report = analyze_script_with_ai(selenium_script)

    for index, (test_case, details) in enumerate(test_cases.items()):
        if index < len(report_data['tests']):
            # Get the outcome from the report_data for the corresponding index
            test_result = "Passed" if report_data['tests'][index]['outcome'] == "passed" else "Failed"
            # Add the Test Result to the test_cases dictionary
            details["Test Result"] = test_result
    
    # Logging awal
    logging.info(f"Generating test report for script:\n{selenium_script[:200]}...")

    # Siapkan direktori untuk menyimpan PDF
    base_dir = Path(__file__).resolve().parent
    pdf_output_path = base_dir / "static" / "reports"
    pdf_output_path.mkdir(parents=True, exist_ok=True)
    pdf_file_path = pdf_output_path / f"{report_name}.pdf"

    # Langkah 3: Membuat PDF dan menyertakan hasil analisis dan tes
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page(orientation='L')  # Menggunakan orientasi landscape
        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(0, 10, f"Test Report: {report_name}", ln=True, align="C")
        pdf.set_font("Arial", size=10)  # Mengurangi ukuran font agar lebih kompak
        pdf.ln(20)
        available_width = 297 - 30  # 15 mm margin on each side

        # Set the column widths as percentages of the available width
        test_case_width = available_width * 0.2  # 20% for Test Case
        description_width = available_width * 0.5  # 50% for Description
        result_width = available_width * 0.3  # 30% for Result

        try:
            summary = report_data.get('summary', {})
            passed = str(summary.get('passed', 'N/A'))  # Default to 'N/A' if key is missing
            total = str(summary.get('total', 'N/A'))
            collected = str(summary.get('collected', 'N/A'))
            duration = str(round(report_data.get('duration', 'N/A'), 1))

            pdf.set_x(110)
            # Add the header row for the table
            pdf.set_fill_color(255, 223, 186)  # Light yellow background for header
            pdf.cell(80, 10, "Summary", 1, 1, 'C', 1)

            pdf.set_x(110)
            pdf.set_fill_color(255, 223, 186)  # Light yellow background for header
            pdf.cell(20, 10, "Passed", 1, 0, 'C', 1)
            pdf.cell(20, 10, "Total", 1, 0, 'C', 1)
            pdf.cell(20, 10, "Collected", 1, 0, 'C', 1)
            pdf.cell(20, 10, "Duration", 1, 1, 'C', 1)

            pdf.set_x(110)
            pdf.set_fill_color(255, 255, 255)
            pdf.cell(20, 10, passed, 1, 0, 'L', 1)
            pdf.cell(20, 10, total, 1, 0, 'L', 1)
            pdf.cell(20, 10, collected, 1, 0, 'L', 1)
            pdf.cell(20, 10, duration, 1, 1, 'L', 1) 

            pdf.ln(10)

        except Exception as e:
            logging.error(f"Failed to save PDF: Failed to save summary {e}")
            raise

        # Add the header row for the table
        pdf.set_fill_color(255, 223, 186)  # Light yellow background for header
        pdf.cell(test_case_width, 10, "Test Case", 1, 0, 'C', 1)
        pdf.cell(description_width, 10, "Description", 1, 0, 'C', 1)
        pdf.cell(result_width, 10, "Result", 1, 1, 'C', 1)

        # Menambahkan data tabel untuk setiap test case
        row_index = 0
        for test_case, details in test_cases.items():
            # Alternate row colors (zebra striping)
            if row_index % 2 == 0:
                pdf.set_fill_color(255, 255, 255)  # White for even rows
            else:
                pdf.set_fill_color(240, 240, 240)  # Light gray for odd rows
            
            # Extract descriptions and details
            description = details.get('Description', 'N/A')
            detailed_desc = f"{details.get('Actual Results', 'N/A')}"
            test_result = f"{details.get('Test Result', 'N/A')}"

            # Add cells for Test Case and Description
            pdf.cell(test_case_width, 10, test_case, 1, 0, 'L', 1)  # Test Case name

            pdf.cell(description_width, 10, description, 1, 0, 'L', 1)  # Description
            
            pdf.cell(result_width, 10, test_result, 1, 1, 'L', 1)  # Wrap Result text
          
            row_index += 1
            
        # Menambahkan laporan dari AI setelah tabel
        pdf.ln(5)  # Jarak setelah tabel

        label_width = available_width * 0.2  # 20% for Label (Detailed Description, Expected Results, etc.)
        content_width = available_width * 0.8  # 80% for Content

        # Add a new line for separation between tables
        pdf.ln(10)

        # Now, we add rows for the details of each test case
        row_index = 0
        for test_case, details in test_cases.items():
            # Alternate row colors (zebra striping)
            if row_index % 2 == 0:
                pdf.set_fill_color(255, 255, 255)  # White for even rows
            else:
                pdf.set_fill_color(240, 240, 240)  # Light gray for odd rows
            
            pdf.set_fill_color(255, 223, 186)  # Light yellow background for header
            pdf.cell(label_width, 10, "Description", 1, 0, 'C', 1)
            pdf.cell(content_width, 10, "Details", 1, 1, 'C', 1)

            pdf.set_fill_color(255, 255, 255)  # White for normal rows

            # Detailed Description
            # pdf.cell(available_width, 10, test_case, 1, 0, 'C', 1)
            pdf.multi_cell(available_width, 10, test_case, 1, 'C', 1)

            # Detailed Description
            test_result = details.get("Test Result", "N/A")
            pdf.cell(label_width, 10, "Test Result", 1, 0, 'L', 1)
            pdf.multi_cell(content_width, 10, test_result, 1, 'L', 1)

            # Detailed Description
            detailed_desc = details.get("Detailed Description", "N/A")
            pdf.cell(label_width, 10, "Detailed Description", 1, 0, 'L', 1)
            pdf.multi_cell(content_width, 10, detailed_desc, 1, 'L', 1)
            
            # Expected Results
            expected_desc = details.get("Expected Results", "N/A")

            # Calculate the number of lines the content will span
            lines = calculate_lines(expected_desc, content_width, 10)

            # Set the height for the cell based on the number of lines
            cell_height = 20 if lines > 1 else 10

            pdf.cell(label_width, cell_height, "Expected Results", 1, 0, 'L', 1)
            pdf.multi_cell(content_width, 10, expected_desc, 1, 'L', 1)

            # Actual Results
            actual_desc = details.get("Actual Results", "N/A")
            pdf.cell(label_width, 20, "Actual Results", 1, 0, 'L', 1)
            pdf.multi_cell(content_width, 10, actual_desc, 1, 'L', 1)

            # Issues Found
            issues_desc = details.get("Issues Found", "N/A")
            pdf.cell(label_width, 10, "Issues Found", 1, 0, 'L', 1)
            pdf.multi_cell(content_width, 10, issues_desc, 1, 'L', 1)

            # Recommendations
            recommendations_desc = details.get("Recommendations", "N/A")
            pdf.cell(label_width, 10, "Recommendations", 1, 0, 'L', 1)
            pdf.multi_cell(content_width, 10, recommendations_desc, 1, 'L', 1)

            # Folder containing screenshots for the current test case
            proof_image_folder = os.path.join("static", "screenshot", f"session_{session_timestamp}")

            # Retrieve all valid image files
            proof_images = [
                os.path.join(proof_image_folder, image)
                for image in sorted(os.listdir(proof_image_folder))
                if image.endswith((".png", ".jpg", ".jpeg")) and image.startswith(f"login") # Adjust condition
            ]

            # Dimensions for each image
            image_width = 120  # Adjust as needed
            image_height = 100  # Adjust as needed

            if proof_images:
                # Label column: spans the total height of all images
                label_total_height = image_height * len(proof_images)

                # Content column: Add all images
                for index, image_path in enumerate(proof_images):
                    if os.path.exists(image_path):
                        # Add cell for the image to maintain structure
                        pdf.cell(available_width, image_height + 10, "", 1, 0, 'C', 1)
                        current_x = pdf.get_x() - available_width  # Align image with the cell
                        current_y = pdf.get_y()  # Current vertical position
                        
                        # Insert the image at the correct coordinates
                        pdf.image(image_path, x=current_x + 80, y=current_y + 2, w=image_width, h=image_height)

                        # Move to the next line after each image
                        pdf.ln(image_height)
            else:
                # If no images, show "No proof"
                pdf.cell(content_width, 10, "No proof", 1, 1, 'C', 1)

            # Add some spacing at the end of the block
            pdf.ln(15)

        # Output file PDF
        pdf.output(str(pdf_file_path))
        logging.info(f"Test report saved as PDF: {pdf_file_path}")
    except Exception as e:
        logging.error(f"Failed to save PDF: {e}")
        raise

    return str(pdf_file_path)

def analyze_script_with_ai(selenium_script):
    """
    Uses AI to analyze the given Selenium script and extract test cases.
    
    Args:
        selenium_script (str): The Selenium script to analyze.
    
    Returns:
        tuple: A tuple containing a list of test cases and the AI-generated test report.
    """
    # Memanggil model AI untuk menganalisis skrip
    messages = [{"role": "user", "content": TEMPLATE_PROMPT_REPORT.format(selenium_script=selenium_script)}]
    ai_report = ""
    test_cases = {}
    
    try:
        for message in client.chat_completion(messages, max_tokens=3000, stream=True, temperature=0.7, top_p=0.95):
            if "choices" in message:
                content = message.choices[0].delta.content
                ai_report += content 
            else:
                logging.warning(f"Unexpected response format: {message}")

        # Process the final ai_report after the streaming ends
        test_case_pattern = r"^\d+\.\s\*\*(Test Case \d+)\*\*:\s*(.+)"
        for line in ai_report.split("\n"):
            match = re.match(test_case_pattern, line)
            if match:
                test_case_name = match.group(1)
                test_case_desc = match.group(2)
                test_cases[test_case_name] = {"Description": test_case_desc}

        # Extract detailed report for each test case
        detailed_report_pattern = r"\*\*(Test Case \d+)\*\*\n- \*\*Description\*\*: (.+?)\n- \*\*Expected Results\*\*: (.+?)\n- \*\*Actual Results\*\*: (.+?)\n- \*\*Issues Found\*\*: (.+?)\n- \*\*Recommendations\*\*: (.+?)\n"

        detailed_reports = re.findall(detailed_report_pattern, ai_report, re.DOTALL)
        for test_case, desc, expected, actual, issues, recommendations in detailed_reports:
            if test_case in test_cases:
                test_cases[test_case].update({
                    "Detailed Description": desc,
                    "Expected Results": expected,
                    "Actual Results": actual,
                    "Issues Found": issues,
                    "Recommendations": recommendations,
                })
            else:
                logging.warning(f"Unexpected response format: {message}")
        if not ai_report.strip():
            raise ValueError("Empty AI report generated.")
        
        logging.info("Test report generated successfully by AI.")
    except Exception as e:
        logging.critical(f"Failed to generate test report from model: {e}")
        raise

    return test_cases, ai_report