from flask import Blueprint, jsonify, request, send_from_directory, \
    current_app
from app.models import User, Hackathon
from app import db
from app.hackathons.utils import allowed_files, save_hkthon_imgs
import os


hackathons = Blueprint('hackathons', __name__)


@hackathons.route('/uploads/hakthon_imgs/<filename>', methods=['GET'])
def get_hakthon_image(filename):
    return send_from_directory(
        os.path.join(
            current_app.config['UPLOAD_FOLDER'], 'hakthon_imgs'), filename)


@hackathons.route('/api/addhackathon', methods=['POST'])
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
                    f"{new_hackathon.title} added"
            }, 201)
    else:
        return jsonify({
            "error": "Allowed file types are jpeg, jpg, png"
        }, 400)


@hackathons.route('/api/participate', methods=['POST'])
def enroll():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Empty JSON object"}, 400)

    user_id = data["user_id"]
    hackathon_id = data["hackathon_id"]

    if not (user_id and hackathon_id):
        return jsonify({"error": "provide both user_id and hackathon_id"}, 200)

    user = User.query.filter_by(public_id=user_id).first()
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
        {"message": f"{user.username} enrolled in {hackathon.title}"}, 200)


@hackathons.route('/api/enrolledHackathons/<string:user_id>', methods=["GET"])
def get_enrolled_hackathons(user_id):
    user = User.query.filter_by(public_id=user_id).first()

    if not user:
        return jsonify({"error": "User not found. Wrong id!"}, 400)

    if user.is_admin:
        return jsonify({"error": "admins do not participate"}, 400)

    hackathons_list = []

    for hackathon in user.participated_hackathons:
        data = {
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


@hackathons.route('/api/unenroll', methods=['POST'])
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
            "message": f"{user.username} unenrolled from {hackathon.title}"
        }, 400)
