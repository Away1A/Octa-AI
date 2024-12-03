from flask import Flask, request, render_template, jsonify, url_for, send_file
from huggingface_hub import InferenceClient
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import glob
import re
import subprocess
import time
import logging
import datetime
from model import db, TestHistory, SeleniumScript, WebElementData
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from flask_socketio import SocketIO, emit
from sqlalchemy import func
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from sqlalchemy.orm import sessionmaker





# Konfigurasi logging
logging.basicConfig(
    level=logging.DEBUG,  # Set level ke DEBUG untuk mencatat semua level
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Inisialisasi Flask dan database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'garuda'
socketio = SocketIO(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:g4rud4inf1nItY2024#@103.171.163.85/automation'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
session_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
screenshot_folder = os.path.join("static", "screenshot", f'session_{session_timestamp}')

db.init_app(app)
migrate = Migrate(app, db)

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

        # Tunggu sampai halaman sepenuhnya dimuat sebelum memulai scraping
        logging.info("Menunggu halaman sepenuhnya dimuat...")
        WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located((By.XPATH, '//*')))
        
        # Mulai proses scraping hanya di halaman target
        elements = driver.find_elements(By.XPATH, '//*')
        if not elements:
            logging.warning("Tidak ada elemen ditemukan di halaman target.")
        
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
                logging.error(f"Gagal memproses elemen dengan XPath {xpath}: {e}")

        # Simpan semua elemen yang ditemukan ke database
        db_session.commit()
        logging.info(f"Berhasil melakukan scraping elemen dari {target_url}.")

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
    element_details = "\n".join([f"{el.attribute}" for el in elements])
    logging.info(f"Total elements retrieved: {len(element_details)}")

    # Buat template prompt
    template_prompt = (
        f"Convert the following Gherkin scenario to a Selenium script using pytest for the URL.\n"
        "Follow these coding guidelines:\n"
        "- Use **XPath** with **multiple `contains(@class, ...)` conditions** to locate button elements with complex class attributes.\n"
        "- Use `//input[@id` or CSS Selectors for element identification.\n"
        "- For password field use Xpath with contains class if dont have Xpath id \n"
        "- For submit or login use Xpath with id"
        "- Use XPath with attributes (if available) or CSS Selector for locating input or button elements.\n"
        "- Use JavaScript Executor to click buttons or elements as required.\n"
        "- Ensure modal pop-ups or overlays are handled correctly by scoping actions within the modal context.\n"
        "- Make sure to use `pytest.fail()` for failures, with descriptive error messages.\n\n"
        "- Use the URL specified in the Gherkin scenario for `driver.get()` instead of hardcoding.\n"
        "- For assertions, validate the current URL (`driver.current_url`) rather than the driver title.\n\n"
        "Gherkin Scenario:\n"
        f"{gherkin_text}\n\n"
        "Available Elements:\n"
        f"{element_details}\n\n"
        "Expected Script Structure:\n"
        "- Create new driver for each test case\n"
        "- Driver Options:\n"
        "  - Use headless mode in driver options for test efficiency.\n"
        "  - Initialize WebDriver with the following service:\n"
        "    `service = Service(executable_path = 'C:\\Program Files\\chromedriver-win64\\chromedriver.exe')`\n"
        "- Implicit Waits:\n"
        "  - Use `WebDriverWait` for dynamic waiting of elements, especially for modals or AJAX-based elements.\n"
        "- Assertions:\n"
        "  - Validate the result of each step (e.g., check URLs, content changes, or modal visibility).\n"
        "- Modal Handling:\n"
        "  - Wait for modal visibility using `visibility_of_element_located`.\n"
        "  - Locate elements within the modal scope using `modal.find_element` or a similar approach to avoid conflicts.\n"
        "  - Ensure modal is dismissed or closed using `invisibility_of_element` after required interactions.\n"
        "- Exception Handling:\n"
        "  - Include exception handling for `TimeoutException`, `NoSuchElementException`, and `UnexpectedAlertPresentException`.\n"
        "  - Take screenshots during exceptions to assist debugging.\n"
        "- Screenshots:\n"
        "  - Save screenshots at key steps:\n"
        "    - After page loads.\n"
        "    - After performing major actions (e.g., submitting a form, interacting with a modal).\n"
        "    - During exceptions or unexpected behaviors.\n"
        "  - Organize screenshots into session-based subfolders:\n"
        "    - Root folder: `static/screenshot`\n"
        "    - Subfolder for each session: timestamp-based naming (e.g., `session_20241121113045`).\n"
        "  - Use Python's `os.makedirs()` to create folders dynamically.\n"
        "- Example for dynamically saving screenshots:\n"
        "  ```python\n"
        "  import os\n"
        "  import time\n"
        "  # Define base directory\n"
        "  base_dir = os.path.join(os.getcwd(), 'static', 'screenshot')\n"
        "  timestamp = time.strftime('%Y%m%d%H%M%S')  # e.g., '20241121113045'\n"
        "  session_dir = os.path.join(base_dir, f'session_{timestamp}')\n"
        "  os.makedirs(session_dir, exist_ok=True)\n"
        "  # Save screenshots in the session folder\n"
        "  driver.save_screenshot(os.path.join(session_dir, 'step_description.png'))\n"
        "  ```\n"
        "- Code Quality:\n"
        "  - Maintain consistent structure with clear variable naming and comments.\n"
        "  - Include detailed error messages in assertions (e.g., `pytest.fail('Expected page did not load.')`).\n"
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
        result = subprocess.run(["pytest", file_name], capture_output=True, text=True)
        logging.info("Pytest executed successfully.")
        return result.stdout
    except Exception as e:
        logging.error(f"Failed to run pytest on {file_name}: {e}")
        return str(e)


@app.route("/index", methods=["GET", "POST"])
def index():
    logging.info("Rendering index page.")
    return render_template("index.html")

@app.route("/")
def dashboard():
    logging.info("Rendering dashboard.")
    return render_template("dashboard.html")

@app.route("/download_report/<filename>")
def download_report(filename):
    report_path = os.path.join("static", "reports", filename)
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True)
    else:
        return "Report not found.", 404
    
@app.route("/test", methods=["GET", "POST"])
def run_tests():
    test_output = ""
    if request.method == "POST":
        file = request.files.get("pytest_file")
        if file and file.filename.endswith(".py"):
            file_name = file.filename
            file.save(file_name)
            logging.info(f"Test file {file_name} saved.")
            test_output = run_pytest(file_name)
            os.remove(file_name)
            logging.info(f"Temporary test file {file_name} removed after execution.")
        else:
            logging.warning("Invalid file format. Please upload a .py file.")
            return "Please upload a valid .py file."
    return render_template("test.html", test_output=test_output)


def generate_test_report(filename, result, execution_time, start_time, end_time, screenshots, log_output=None):
    # Nama file PDF
    pdf_filename = f"test_report_{filename}.pdf"
    
    # Buat dokumen PDF
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Header
    elements.append(Paragraph("Automated Test Report", styles['Title']))
    elements.append(Spacer(1, 12))

    # Informasi Pengujian
    elements.append(Paragraph("<b>Test Details:</b>", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    data = [
        ["Filename", filename],
        ["Result", result.capitalize()],
        ["Execution Time (seconds)", f"{execution_time:.2f}"],
        ["Start Time", start_time.strftime("%Y-%m-%d %H:%M:%S")],
        ["End Time", end_time.strftime("%Y-%m-%d %H:%M:%S")],
    ]
    table = Table(data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 24))

    # Daftar Screenshot
    if screenshots:
        elements.append(Paragraph("<b>Screenshots:</b>", styles['Heading2']))
        elements.append(Spacer(1, 12))
        for screenshot in screenshots:
            img_path = os.path.join("static", screenshot)
            if os.path.exists(img_path):
                elements.append(Image(img_path, width=300, height=150))
                elements.append(Spacer(1, 12))
            else:
                elements.append(Paragraph(f"Image not found: {screenshot}", styles['Normal']))
                elements.append(Spacer(1, 12))
        elements.append(Spacer(1, 24))

    # Log Output
    if log_output:
        elements.append(Paragraph("<b>Test Log:</b>", styles['Heading2']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(log_output.replace("\n", "<br/>"), styles['Normal']))
        elements.append(Spacer(1, 24))

    # Build PDF
    doc.build(elements)
    return pdf_filename


@app.route("/one_click", methods=["GET", "POST"])
def one_click():
    test_output = ""
    test_history = TestHistory.query.all()
    gherkin_files = SeleniumScript.query.with_entities(SeleniumScript.filename).all()
    gherkin_content = ""
    selenium_script = ""
    screenshots = []  # Variabel untuk menyimpan daftar screenshot
    screenshot_base_folder = os.path.join("static", "screenshot")
    test_history_entry = None  # Inisialisasi variabel sebelum digunakan


    if request.method == "POST":
        logging.info("Received POST request in one_click.")

        # Mendapatkan file dan URL dari form
        file = request.files.get("feature_file")
        login_url = request.form.get("url")
        target_url = request.form.get("target_url")

        # Langkah 1: Memeriksa apakah login_url dan target_url sudah ada di WebElementData
        existing_elements = WebElementData.query.filter_by(url=target_url).first()

        if login_url and target_url and not existing_elements:
            logging.info(f"Scraping elements for target_url: {target_url}")
            scrape_elements(login_url, target_url, db.session)

        # Langkah 2: Proses file .feature
        if file and file.filename.endswith(".feature"):
            logging.debug(f"Feature file uploaded: {file.filename}")
            existing_script = SeleniumScript.query.filter_by(filename=file.filename).first()

            if existing_script:
                logging.info(f"Using existing script for {file.filename}.")
                selenium_script = existing_script.script_content
                test_output = "Using existing Selenium script from database."

                # Buat file sementara untuk menjalankan script
                file_name = "temp_selenium_test.py"
                with open(file_name, "w") as f:
                    f.write(selenium_script)

                # Catat waktu mulai
                start_time = datetime.datetime.now()

                # Jalankan tes menggunakan pytest
                test_output += "\n" + run_pytest(file_name)

                # Menunggu sampai screenshot tersedia dan menyimpannya ke dalam database
                latest_folder = get_latest_session_folder(screenshot_base_folder)
                if latest_folder:
                    # Cari semua screenshot di folder terbaru
                    screenshot_files = glob.glob(os.path.join(latest_folder, "*.png"))
                    
                    # Tunggu sampai screenshot tersedia
                    while not screenshot_files:
                        logging.debug("Waiting for screenshots to be saved...")
                        time.sleep(1)  # Tunggu sebentar sebelum mencoba lagi
                        screenshot_files = glob.glob(os.path.join(latest_folder, "*.png"))
                    
                    # Membuat daftar URL screenshot
                    screenshots = [
                        url_for('static', filename=os.path.relpath(file, start="static").replace("\\", "/"))
                        for file in screenshot_files
                    ]
                    logging.info(f"Screenshots found: {screenshots}")

                else:
                    logging.warning("No session folders found.")

                # Catat waktu selesai
                end_time = datetime.datetime.now()

                # Hitung waktu eksekusi
                execution_time = (end_time - start_time).total_seconds()
                logging.debug(f"Execution time: {execution_time} seconds.")

                # Tentukan hasil tes
                result = "passed" if "passed" in test_output else "failed"

                if result == "passed":
                    # Buat laporan PDF setelah screenshot tersedia
                    pdf_filename = generate_test_report(
                        file.filename,
                        result,
                        execution_time,
                        start_time,
                        datetime.datetime.now(),
                        screenshots
                    )
                    logging.info(f"Test report generated: {pdf_filename}")

                # Simpan hasil tes ke database
                test_history_entry = TestHistory(
                    filename=file.filename,
                    result=result,
                    execution_time=execution_time,
                    start_time=start_time,
                    end_time=end_time,
                    screenshots=screenshots
                )
                db.session.add(test_history_entry)
                db.session.commit()

                if result == "passed":
                    existing_script.status = "passed"

                db.session.commit()
                os.remove(file_name)
                logging.debug(f"Temporary file {file_name} removed.")

            else:
                # Jika tidak ada script yang ada di database, buat script baru
                try:
                    gherkin_content = file.read().decode("utf-8")
                    logging.info(f"Feature file content read successfully: {file.filename}")

                    use_template_prompt = "use_template_prompt" in request.form
                    raw_selenium_script = generate_selenium_script(
                        gherkin_content, login_url, target_url, use_template=use_template_prompt
                    )
                    cleaned_script = clean_code_with_regex(raw_selenium_script)
                    selenium_script = cleaned_script

                    # Buat file sementara untuk menjalankan script
                    file_name = "temp_selenium_test.py"
                    with open(file_name, "w") as f:
                        f.write(cleaned_script)

                    # Jalankan tes menggunakan pytest
                    start_time = datetime.datetime.now()
                    test_output = run_pytest(file_name)
                    execution_time = (datetime.datetime.now() - start_time).total_seconds()

                    # Menunggu sampai screenshot tersedia dan menyimpannya ke dalam database
                    latest_folder = get_latest_session_folder(screenshot_base_folder)
                    if latest_folder:
                        screenshot_files = glob.glob(os.path.join(latest_folder, "*.png"))
                        while not screenshot_files:
                            logging.debug("Waiting for screenshots to be saved...")
                            time.sleep(1)  # Tunggu sebentar sebelum mencoba lagi
                            screenshot_files = glob.glob(os.path.join(latest_folder, "*.png"))
                        screenshots = [
                            url_for('static', filename=os.path.relpath(file, start="static").replace("\\", "/"))
                            for file in screenshot_files
                        ]
                        logging.info(f"Screenshots found: {screenshots}")

                        if test_history_entry:  # Pastikan hanya menggunakan variabel jika sudah diinisialisasi
                            test_history_entry.screenshots = screenshots
                    else:
                        logging.warning("No session folders found.")

                    result = "passed" if "passed" in test_output else "failed"

                    if result == "passed":
                        pdf_filename = generate_test_report(
                            file.filename,
                            result,
                            execution_time,
                            start_time,
                            datetime.datetime.now(),
                            screenshots
                        )
                        logging.info(f"Test report generated: {pdf_filename}")

                    test_history_entry = TestHistory(
                        filename=file.filename,
                        result=result,
                        execution_time=execution_time,
                        start_time=start_time,
                        end_time=datetime.datetime.now(),
                        screenshots=screenshots
                    )
                    db.session.add(test_history_entry)
                    db.session.commit()                    # Hanya simpan SeleniumScript jika hasilnya "passed"
                    if result == "passed":
                        selenium_script_entry = SeleniumScript(
                            filename=file.filename,
                            script_content=cleaned_script,
                            status="passed"
                        )
                        db.session.add(selenium_script_entry)

                    db.session.commit()
                    os.remove(file_name)
                    logging.debug(f"Temporary file {file_name} removed.")

                except Exception as e:
                    logging.error(f"Error processing uploaded file: {e}")
                    return "Failed to process the uploaded feature file."

        else:
            logging.warning("Invalid file format or no file uploaded.")
            return "Please upload a valid .feature file."

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            updated_test_history = TestHistory.query.order_by(TestHistory.start_time.desc()).all()
            history_data = [
                {
                    "filename": test.filename,
                    "result": test.result,
                    "execution_time": "{:.2f}".format(test.execution_time),
                    "start_time": test.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": test.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "screenshots": test.screenshots.split(",") if test.screenshots else []  

                }
                for test in updated_test_history
            ]
            pdf_filename = f"test_report_{file.filename}.pdf"  # Nama file PDF yang dibuat
            return jsonify({
                "gherkin_content": gherkin_content,
                "selenium_script": selenium_script,
                "test_output": test_output,
                "test_history": history_data,
                "screenshots": screenshots,
                "pdf_report": pdf_filename  
            })

        return render_template(
            "one_click.html",
            test_history=test_history,
            gherkin_files=gherkin_files,
            gherkin_content=gherkin_content,
            selenium_script=selenium_script,
            test_output=test_output,
            screenshots=screenshots,
            pdf_report=pdf_filename,
        )

    return render_template("one_click.html", test_history=test_history, gherkin_files=gherkin_files)

# WebSocket event to handle real-time communication
@socketio.on('run_test')
def handle_test_run(data):
    logging.info("Test run started via WebSocket")
    test_output = run_pytest("temp_selenium_test.py")
    emit('test_result', {'output': test_output})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=False)
