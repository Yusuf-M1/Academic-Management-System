import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-academic-key'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'yusuf' # Update this!
    MYSQL_DB = 'academic_management'