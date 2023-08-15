from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os
from flask_bcrypt import Bcrypt
from app.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)
    UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'hakthon_imgs'), exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'submission_files'), exist_ok=True)

    from app.main.views import main
    from app.users.views import users
    from app.hackathons.views import hackathons
    from app.submissions.views import submissions

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(hackathons)
    app.register_blueprint(submissions)

    return app
