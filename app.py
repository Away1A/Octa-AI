from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
import logging
from config import Config

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
app.config.from_object(Config)

socketio = SocketIO(app)
session_timestamp = app.config['SESSION_TIMESTAMP']
screenshot_folder = app.config['SCREENSHOT_FOLDER']

from model import db

db.init_app(app)
migrate = Migrate(app, db)

# WebSocket event to handle real-time communication
@socketio.on('run_test')
def handle_test_run(data):
    logging.info("Test run started via WebSocket")
    test_output = run_pytest("temp_selenium_test.py")
    emit('test_result', {'output': test_output})

if __name__ == '__main__':
    from routes import * 
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=False)
