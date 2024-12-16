import os
import datetime 

class Config:
    SECRET_KEY = 'garuda'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:g4rud4inf1nItY2024#@103.171.163.85/automation'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Generate session-based screenshot folder dynamically
    SESSION_TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    SCREENSHOT_FOLDER = os.path.join("static", "screenshot", f'session_{SESSION_TIMESTAMP}')
