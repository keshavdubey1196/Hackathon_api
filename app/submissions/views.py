from flask import jsonify, request, send_from_directory, Blueprint, \
                  current_app
from app import db
from app.models import User, Hackathon, Submission
import os
from app.submissions.utils import save_submisssion_files, allowed_files


submissions = Blueprint('submissions', __name__)


@submissions.route('/uploads/submission_files/<filename>', methods=['GET'])
def get_submisssion_files(filename):
    return send_from_directory(
        os.path.join(
            current_app.config['UPLOAD_FOLDER'], 'submission_files'), filename)


@submissions.route('/api/submission', methods=['POST'])
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


@submissions.route('/api/user_submissions/<int:user_id>', methods=["GET"])
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
