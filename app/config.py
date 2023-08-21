from dotenv import load_dotenv
import os

load_dotenv()

# db_user = os.environ['DB_USER']
# db_password = os.environ['DB_PASSWORD']
# db_host = os.environ['DB_HOST']
# db_port = os.environ['DB_PORT']
# db_name = os.environ['DB_NAME']
# SQLALCHEMY_DATABASE_URI = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    FLASK_DEBUG = True
    # DB_USER = 'postgres'
    # DB_PASSWORD = os.environ["DB_PASSWORD"]
    # DB_HOST = 'localhost'
    # DB_PORT = 5432
    # DB_NAME = 'structured_hackathon_api'
