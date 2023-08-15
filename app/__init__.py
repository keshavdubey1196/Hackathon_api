from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from dotenv import load_dotenv
import os
from flask_bcrypt import Bcrypt
from app.config import DATABASE_URI


load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
db = SQLAlchemy(app)


bcrypt = Bcrypt(app)
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# create folders if they don't exist in project
os.makedirs(os.path.join(UPLOAD_FOLDER, 'hakthon_imgs'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'submission_files'), exist_ok=True)



from app import views