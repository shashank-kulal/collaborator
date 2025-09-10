import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Existing SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///default.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Add MySQL configuration for API endpoints
    DB_HOST = os.getenv('DB_HOST', 'vefogix-mysql-vefogix.d.aivencloud.com')
    DB_PORT = int(os.getenv('DB_PORT', 12395))
    DB_NAME = os.getenv('DB_NAME', 'defaultdb')
    DB_USER = os.getenv('DB_USER', 'avnadmin')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'AVNS_uD1hFc3OPe9G-2EuuYv')