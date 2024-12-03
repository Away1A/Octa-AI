from flask_sqlalchemy import SQLAlchemy
import datetime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base() 
db = SQLAlchemy()

class TestHistory(db.Model):
    __tablename__ = 'test_history'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    result = db.Column(db.String(50), nullable=False)
    execution_time = db.Column(db.Float, nullable=False)
    
    start_time = db.Column(db.DateTime, nullable=False)  
    end_time = db.Column(db.DateTime, nullable=False)    
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    screenshots = db.Column(db.Text, nullable=True)  

    # Metode untuk mengonversi objek menjadi dictionary
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "result": self.result,
            "execution_time": self.execution_time,
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": self.end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }



class SeleniumScript(db.Model):
    __tablename__ = 'selenium_script'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=True)
    script_content = db.Column(db.Text, nullable=False)
    
    # Kolom tambahan
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

class WebElementData(db.Model):
    __tablename__ = 'web_element_data'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(2083), nullable=False)  
    xpath = db.Column(db.String(500), nullable=False)  
    attribute = db.Column(db.String(500), nullable=True)  
    text_content = db.Column(db.Text, nullable=True)  
