from app import app, bcrypt, db
from flask import jsonify, request, send_from_directory
from app.models import User, Hackathon
import ast
# from werkzeug.utils import secure_filename
import secrets
import os
from PIL import Image


def allowed_files(filename, allowd_exts):
    try:
        is_dot_in_filename = '.' in filename
        if_ext_in_allowed_exts = filename.rsplit(
            '.', 1)[1].lower() in allowd_exts

        return if_ext_in_allowed_exts and is_dot_in_filename
    except Exception:
        return False


def save_hkthon_imgs(file):
    random_hex = secrets.token_hex(8)
    _, ext = os.path.splitext(file.filename)
    picture_fn = random_hex + ext
    picture_path = os.path.join(
        app.config['UPLOAD_FOLDER'], 'hakthon_imgs', picture_fn)
    output_size = (200, 200)
    new_file = Image.open(file)
    new_file.thumbnail(output_size)
    new_file.save(picture_path)

    return picture_fn


@app.route('/uploads/hakthon_imgs/<filename>', methods=['GET'])
def get_hakthon_image(filename):
    return send_from_directory(
        os.path.join(app.config['UPLOAD_FOLDER'], 'hakthon_imgs'), filename)


@app.route('/info', methods=['GET'])
def info():
    return "<h1>This is home route</h1>"


@app.route('/api/users', methods=["GET"])
def getUsers():
    users = User.query.all()
    user_list = []

    # serializing each user and adding to list
    for user in users:
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        }
        user_list.append(user_data)

    return jsonify(user_list, 200)


@app.route('/api/users/<int:user_id>', methods=["GET"])
def getUserById(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({"error": "user does not exists"}, 404)

    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
    }
    return jsonify(user_data, 200)


@app.route('/api/adduser', methods=["POST"])
def addUser():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Empty JSON object"}, 400)
    # getting user data from JSON
    name = data["name"]
    email = data["email"]
    password = data["password"]
    is_admin_str = data.get('is_admin', "False")

    # to safely convert is_admin_str to bool
    try:
        is_admin = ast.literal_eval(is_admin_str)
    except (ValueError, SyntaxError):
        return jsonify({"error": "Invalid value for is_admin"})

    # validating required fields
    if not name or not email or not password:
        return jsonify(
            {
                "error": "Name, email and passoword are required fields"
            }, 400)

    # to check if user exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({
            "error": "User exists with same email"
        }, 409)

    # encrypt the password
    cipher_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = User(name=name, email=email,
                    password=cipher_password, is_admin=is_admin)

    db.session.add(new_user)
    db.session.commit()

    return jsonify(
        {
            "message": f"{new_user.name} with id = {new_user.id} added "
        }, 201)


@app.route('/api/getuserhackathons/<int:user_id>', methods=['GET'])
def get_user_created_hackathons(user_id):
    user = User.query.filter_by(id=user_id).first()
    hackathons_list = []

    for hackathon in user.created_hackathons:
        data = {
            "id": hackathon.id,
            "title": hackathon.title,
            "description": hackathon.description,
            "bg_image": f"/uploads/hakthon_imgs/{hackathon.bg_image}",
            "hakthon_img": f"/uploads/hakthon_imgs/{hackathon.hakthon_img}",
            "submission_type": hackathon.submission_type,
            "rewards": hackathon.rewards,
            "created_at": hackathon.created_at,
            "start_datetime": hackathon.start_datetime,
            "end_datetime": hackathon.end_datetime,
            "creator_id": hackathon.creator_id
        }
        hackathons_list.append(data)

    return jsonify(hackathons_list, 200)


@app.route('/api/addhackathon', methods=['POST'])
def add_hackathon():
    data = request.form
    if not data:
        return jsonify({"error": "Empty form sent"}, 400)

    title = data['title']
    description = data.get('description', 'OK')
    submission_type = data.get('submission_type', 'file')
    rewards = data.get('rewards', 500)
    start_datetime = data['start_datetime']
    end_datetime = data['end_datetime']
    creator_id = data['creator_id']
    bg_image = request.files['bg_image']
    hakthon_img = request.files['hakthon_img']

    # check if required data is provided
    if not (
            title and
            start_datetime and
            end_datetime and
            bg_image and
            hakthon_img):

        data = {
            "title": "required",
            "start_datetime": "required",
            "end_datetime": "required",
            "bg_image": "required",
            "hakthon_img": "required",
            "creator_id": "required"
        }
        return jsonify(data, 400)

    if (bg_image.filename == "") or (hakthon_img.filename == ""):
        # print(bg_image.filename)
        # print(hakthon_img.filename)
        return jsonify({"error": "images provided must have filename"}, 400)

    allowed = allowed_files(bg_image.filename, ['jpeg', 'jpg', 'png']) and \
        allowed_files(hakthon_img.filename, ['jpeg', 'jpg', 'png'])

    if allowed:
        bg_image_filename = save_hkthon_imgs(bg_image)
        hakthon_img_filename = save_hkthon_imgs(hakthon_img)
        new_hackathon = Hackathon(
            title=title,
            description=description,
            bg_image=bg_image_filename,
            hakthon_img=hakthon_img_filename,
            submission_type=submission_type,
            rewards=rewards,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            creator_id=creator_id
        )
        db.session.add(new_hackathon)
        db.session.commit()
        return jsonify(
            {
                "message":
                    f"{new_hackathon.title} added id = {new_hackathon.id}"
                }, 201)
    else:
        return jsonify({
            "error": "Allowed file types are jpeg, jpg, png"
        }, 400)
