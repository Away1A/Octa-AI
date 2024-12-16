import datetime
import glob
import time
from flask import Flask, request, render_template, jsonify, url_for, send_file
from model import db, TestHistory, SeleniumScript, WebElementData
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from flask_socketio import SocketIO, emit
import logging
from services import generate_selenium_script, scrape_elements, clean_code_with_regex, read_gherkin_file, get_element_xpath, get_latest_session_folder, run_pytest, generate_test_report
from app import app
import os
import datetime

session_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
screenshot_folder = os.path.join("static", "screenshot", f'session_{session_timestamp}')

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

@app.route("/one_click", methods=["GET", "POST"])
def one_click():
    result = "failed"
    test_output = ""
    test_history = TestHistory.query.all()
    gherkin_files = SeleniumScript.query.with_entities(SeleniumScript.filename).all()
    gherkin_content = ""
    selenium_script = ""
    screenshots = []  # Variabel untuk menyimpan daftar screenshot
    screenshot_base_folder = os.path.join("static", "screenshot")
    test_history_entry = None  # Inisialisasi variabel sebelum digunakan
    execution_time = 0


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

                start_time = datetime.datetime.now()

                # Jalankan tes menggunakan pytest dan dapatkan laporan JSON
                report_data = run_pytest(file_name)

                # Simpan laporan JSON langsung tanpa pengecekan
                test_output = report_data
                result = "completed"  # Tetapkan status sebagai "completed"
                execution_time = (datetime.datetime.now() - start_time).total_seconds()

                    # Generate PDF report untuk hasil "passed"
                report_name = file.filename.split('.')[0]
                try:
                            pdf_filename = generate_test_report(
                                selenium_script,
                                report_name,
                                use_template=True
                            )
                            logging.info(f"Test report generated: {pdf_filename}")
                except Exception as e:
                            logging.error(f"Failed to generate test report: {e}")
                            
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

                else:
                    logging.warning("No session folders found.")

                # Catat waktu selesai
                end_time = datetime.datetime.now()

                # Hitung waktu eksekusi
                execution_time = (end_time - start_time).total_seconds()
                logging.debug(f"Execution time: {execution_time} seconds.")

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
                        
                    start_time = datetime.datetime.now()

                    # Jalankan tes menggunakan pytest dan dapatkan laporan JSON
                    report_data = run_pytest(file_name)

                    # Simpan laporan JSON langsung tanpa pengecekan
                    test_output = report_data
                    result = "completed"  # Tetapkan status sebagai "completed"
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

                    # Menyimpan hasil hanya jika "passed"
                    if result == "passed":
                        selenium_script_entry = SeleniumScript(
                            filename=file.filename,
                            script_content=cleaned_script,
                            status="passed"
                        )
                        db.session.add(selenium_script_entry)

                        # Generate PDF report untuk hasil "passed"
                        report_name = file.filename.split('.')[0]
                        try:
                            pdf_filename = generate_test_report(
                                selenium_script,
                                report_name,
                                use_template=True
                            )
                            logging.info(f"Test report generated: {pdf_filename}")
                        except Exception as e:
                            logging.error(f"Failed to generate test report: {e}")

                    # Simpan hasil tes ke dalam TestHistory
                    test_history_entry = TestHistory(
                        filename=file.filename,
                        result=result,
                        execution_time=execution_time,
                        start_time=start_time,
                        end_time=datetime.datetime.now(),
                        screenshots=",".join(screenshots)
                    )
                    db.session.add(test_history_entry)
                    db.session.commit()

                    os.remove(file_name)
                    logging.debug(f"Temporary file {file_name} removed.")

                except Exception as e:
                    logging.error(f"Error processing uploaded file: {e}")
                    return "Failed to process the uploaded feature file."

        else:
            logging.warning("Invalid file format or no file uploaded.")
            return "Please upload a valid .feature file."

        # Response untuk AJAX jika diminta
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
            pdf_filename = f"test_report_{file.filename}.pdf" 
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