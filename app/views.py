from app import app, bcrypt, db
from flask import jsonify, request, send_from_directory
from app.models import User, Hackathon, Submission
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


def save_submisssion_files(file):
    random_hex = secrets.token_hex(8)
    _, ext = os.path.splitext(file.filename)
    if str(ext) in ['.png', '.jpg', '.jpeg']:
        picture_fn = random_hex + ext
        picture_path = os.path.join(
            app.config['UPLOAD_FOLDER'], 'submission_files', picture_fn)
        output_size = (200, 200)
        new_file = Image.open(file)
        new_file.thumbnail(output_size)
        new_file.save(picture_path)
        return picture_fn
    else:
        fn = random_hex + ext
        f_path = os.path.join(
            app.config['UPLOAD_FOLDER'], 'submission_files', fn)
        file.save(f_path)
        return fn


@app.route('/uploads/hakthon_imgs/<filename>', methods=['GET'])
def get_hakthon_image(filename):
    return send_from_directory(
        os.path.join(app.config['UPLOAD_FOLDER'], 'hakthon_imgs'), filename)


@app.route('/uploads/submission_files/<filename>', methods=['GET'])
def get_submisssion_files(filename):
    return send_from_directory(
        os.path.join(
            app.config['UPLOAD_FOLDER'], 'submission_files'), filename)


@app.route('/info', methods=['GET'])
def info():
    return "<h1>This is home route</h1>"





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


@app.route('/api/participate', methods=['POST'])
def enroll():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Empty JSON object"}, 400)

    user_id = data["user_id"]
    hackathon_id = data["hackathon_id"]

    if not (user_id and hackathon_id):
        return jsonify({"error": "provide both user_id and hackathon_id"}, 200)

    user = User.query.filter_by(id=user_id).first()
    hackathon = Hackathon.query.filter_by(id=hackathon_id).first()

    if user.is_admin:
        return jsonify({"error": "admins cannot participate"}, 400)

    if user is None or hackathon is None:
        return jsonify(
            {
                "error": "User or Hackathon or both not Found! Wrong Id(s)."
            }, 400)

    # is user already enrolled in hackathon
    if hackathon in user.participated_hackathons:
        return jsonify({
            "error": "User already in participating in this hackathon"
        }, 400)

    # add user to list of hackathons
    user.participated_hackathons.append(hackathon)
    db.session.commit()

    return jsonify(
        {"message": f"{user.name} enrolled in {hackathon.title}"}, 200)


@app.route('/api/enrolledHackathons/<int:user_id>', methods=["GET"])
def get_enrolled_hackathons(user_id):
    if user_id != int(user_id):
        return jsonify({"message": "Provide an integer user_id"}, 400)

    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({"error": "User not found. Wrong id!"}, 400)

    if user.is_admin:
        return jsonify({"error": "admins do not participate"}, 400)

    hackathons_list = []

    for hackathon in user.participated_hackathons:
        data = {
            "id": hackathon.id,
            "title": hackathon.title,
            "description": hackathon.description,
            "bg_image": f"/uploads/bg_imgs/{hackathon.bg_image}",
            "hakthon_img": f"/uploads/hakthon_imgs/{hackathon.hakthon_img}",
            "rewards": hackathon.rewards,
            "created_at": hackathon.created_at,
            "start_datetime": hackathon.start_datetime,
            "end_datetime": hackathon.end_datetime, }
        hackathons_list.append(data)

    return jsonify(hackathons_list, 200)


@app.route('/api/unenroll', methods=['POST'])
def unenroll():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Empty JSON object"}, 400)

    user_id = data["user_id"]
    hackathon_id = data["hackathon_id"]

    is_userid = user_id == int(user_id)
    is_hackathon_id = hackathon_id == int(hackathon_id)

    if not (is_userid and is_hackathon_id):
        return jsonify(
            {
                "message": "Provide a valid integer user_id and hackathon_id"
            }, 200)

    user = User.query.filter_by(id=user_id).first()
    hackathon = Hackathon.query.filter_by(id=hackathon_id).first()

    if user is None or hackathon is None:
        return jsonify(
            {
                "error": "User or Hackathon or both not Found! Wrong Id(s)."
            }, 400)

    if user.is_admin:
        return jsonify(
            {
                "error": "admins are not enrolled in any hackathons"
            }, 400)

    user.participated_hackathons.remove(hackathon)
    db.session.commit()

    return jsonify(
        {
            "message": f"{user.name} unenrolled from {hackathon.title}"
        }, 400)


@app.route('/api/submission', methods=['POST'])
def submission():
    data = request.form

    if not data:
        return jsonify({"error": "Empty form sent"}, 400)

    user_id = data['user_id']
    hackathon_id = data['hackathon_id']
    file = request.files['file']
    url = data['url']

    # check if all required fields are provided
    if not (user_id and hackathon_id and (file and url)):
        return jsonify(
            {
                "error":
                "user_id,hackathon_id and either file or url is required!"
            }, 400)

    user = User.query.filter_by(id=user_id).first()
    hackathon = Hackathon.query.filter_by(id=hackathon_id).first()

    if not user or not hackathon:
        return jsonify(
            {
                "error": "user or hackathon not found. Wrong id(s) provided"
            }, 400)

    # check if user is admin
    if user.is_admin:
        return jsonify({"error": "admins cannot submit or participate"}, 400)

    hackathons_participated = user.participated_hackathons
    if hackathon not in hackathons_participated:
        return jsonify({
            "error": "You have not participated, therefore cannot submit"
        }, 400)

    # existing submisssion
    existing_submission = Submission.query.filter_by(
        user_id=user_id, hackathon_id=hackathon_id).first()
    if existing_submission:
        return jsonify(
            {
                "error": "User already have submitted on this hackathon"
            }, 409)

    if not allowed_files(file.filename, ['pdf', 'png', 'jpg', 'jpeg']):
        return jsonify(
            {
                "error":
                "Invalid file type. Allowed are jpg, jpeg, pdf, png, pdf"
            }, 400)

    sub_type = hackathon.submission_type.lower()

    if sub_type == "file":
        if allowed_files(file.filename, ['pdf']):
            filename = save_submisssion_files(file)
            new_submission = Submission(
                file=filename,
                url="None",
                user_id=user_id,
                hackathon_id=hackathon_id
            )
        else:
            return jsonify({
                "error": "This hackathon only accepts pdf files"
            }, 400)

    elif sub_type == "image":
        if allowed_files(file.filename, ['jpg', 'jpeg', 'png']):
            filename = save_submisssion_files(file)
            new_submission = Submission(
                file=filename,
                url="None",
                user_id=user_id,
                hackathon_id=hackathon_id
            )
        else:
            return jsonify({
                "error":
                "This hackathon accepts images in format jpg, jpeg and png"
            }, 400)
    elif sub_type == 'url':
        if url != str(url):
            return jsonify({
                "error": "This hackathon accepts url. Provide a url"
            })
        else:
            new_submission = Submission(
                file='None',
                url=url,
                user_id=user_id,
                hackathon_id=hackathon_id
            )

    else:
        return jsonify(
            {
                "error": "invalid submission type for this hackathon"
            }, 400)
    db.session.add(new_submission)
    db.session.commit()

    return jsonify(
        {
            "message":
            f"{user.name} submitted to {hackathon.title} suceessfully"
        }, 200)


@app.route('/api/user_submissions/<int:user_id>', methods=["GET"])
def get_user_submissions(user_id):
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({'error': "User not found"}, 404)

    enrolled_hackathons = user.participated_hackathons
    user_submissions = []

    for hackathon in enrolled_hackathons:
        submissions = Submission.query.filter_by(
            user_id=user_id, hackathon_id=hackathon.id
        ).all()

        for submission in submissions:
            user_submission = {
                "id": submission.id,
                "file": f"/uploads/submission_files/{submission.file}",
                "url": submission.url,
                "created_at": submission.created_at,
                "hackathon_title": hackathon.title,
                "hackathon_id": hackathon.id
            }
            user_submissions.append(user_submission)

    return jsonify(user_submissions, 200)
