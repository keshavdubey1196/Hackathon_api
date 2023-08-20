from flask import Blueprint, jsonify, request
# from flask import make_response, current_app
from app.models import User, Submission
import ast
from app import db, bcrypt
# import datetime
# import jwt
import uuid
from app.submissions.utils import delete_submission_file
from app.hackathons.utils import delete_hkthon_imgs
# from functools import wraps


users = Blueprint('users', __name__)


# def token_required(f):
#     @wraps(f)
#     def decorator(*args, **kwargs):
#         token = None
#         if 'x-access-token' in request.headers:
#             token = request.headers['x-access-token']
#         if not token:
#             return jsonify({
#                 "message": "Token missing"
#             }, 401)
#         try:
#             data = jwt.decode(token, current_app.config['SECRET_KEY'])
#             current_user = User.query.filter_by(
#                 public_id=data['public_id']).first()
#         except Exception:
#             return jsonify({
#                 "message": "Token invalid"
#             }, 401)
#         return f(current_user, *args, **kwargs)


@users.route('/api/users', methods=["GET"])
def getUsers():
    users = User.query.all()
    user_list = []
    # serializing each user and adding to list
    for user in users:
        user_data = {
            "username": user.username,
            "email": user.email,
            "id": user.public_id
        }
        user_list.append(user_data)

    return jsonify(user_list, 200)


@users.route('/api/users/<int:user_id>', methods=["GET"])
def getUserById(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({"error": "user does not exists"}, 404)

    user_data = {
        "username": user.username,
        "email": user.email,
    }
    return jsonify(user_data, 200)


@users.route('/api/user', methods=["POST"])
def addUser():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Empty JSON object"}, 400)
    # getting user data from JSON
    username = data["username"]
    email = data["email"]
    password = data["password"]
    is_admin_str = data.get('is_admin', "False")

    # to safely convert is_admin_str to bool
    try:
        is_admin = ast.literal_eval(is_admin_str)
    except (ValueError, SyntaxError):
        return jsonify({"error": "Invalid value for is_admin"})

    # validating required fields
    if not username or not email or not password:
        return jsonify(
            {
                "error": "username, email and passoword are required fields"
            }, 400)

    # to check if user exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({
            "error": "User exists with same email"
        }, 409)

    # encrypt the password
    cipher_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = User(public_id=str(uuid.uuid4()),
                    username=username,
                    email=email,
                    password=cipher_password,
                    is_admin=is_admin)

    db.session.add(new_user)
    db.session.commit()

    return jsonify(
        {
            "message": f"{new_user.username} added "
        }, 201)


@users.route('/api/getuserhackathons/<string:user_id>', methods=['GET'])
def get_user_created_hackathons(user_id):
    user = User.query.filter_by(public_id=user_id).first()
    if not user:
        return jsonify({
            "error": "User does not exists"
        }, 401)
    hackathons_list = []

    for hackathon in user.created_hackathons:
        data = {
            "title": hackathon.title,
            "description": hackathon.description,
            "bg_image": f"/uploads/hakthon_imgs/{hackathon.bg_image}",
            "hakthon_img": f"/uploads/hakthon_imgs/{hackathon.hakthon_img}",
            "submission_type": hackathon.submission_type,
            "rewards": hackathon.rewards,
            "created_at": hackathon.created_at,
            "start_datetime": hackathon.start_datetime,
            "end_datetime": hackathon.end_datetime,
            "creator_id": user.public_id
        }
        hackathons_list.append(data)

    return jsonify(hackathons_list, 200)


@users.route('/api/deleteuser/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    # Query the database to find the user by their ID
    user = User.query.filter_by(public_id=user_id).first()

    if user is None:
        return jsonify({'message': 'User not found'}, 404)
    created_hackathons = user.created_hackathons
    # for admin user
    if created_hackathons:
        for hackathon in created_hackathons:
            submissions = Submission.query.filter_by(
                hackathon_id=hackathon.id).all()

            for submission in submissions:
                delete_submission_file(submission.file)
                db.session.delete(submission)
            delete_hkthon_imgs(hackathon.bg_image)
            delete_hkthon_imgs(hackathon.hakthon_img)
            db.session.delete(hackathon)
    # for normal user
    user_submissions = Submission.query.filter_by(
        user_id=user.public_id).all()
    if user_submissions:
        for submission in user_submissions:
            delete_submission_file(submission.file)
            db.session.delete(submission)
    try:
        # Delete the user from the database
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted'}, 200)
    except Exception:
        # Handle any errors that may occur during deletion
        db.session.rollback()
        return jsonify({'message': 'Error deleting user'}, 500)


# @users.route('/api/login', methods=['GET'])
# def login():
#     auth = request.authorization
#     if not auth or not auth.username or not auth.password:
#         return make_response(
#             'Could not verify', 401, {
#                 'WWW-Authentication': "Basic realm='login req'"})

#     user = User.query.filter_by(username=auth.username).first()
#     if not user:
#         return make_response(
#             'Could not verify', 401, {
#                 'WWW-Authentication': "Basic realm='login req'"})
#     if bcrypt.check_password_hash(user.password, auth.password):
#         token = jwt.encode(
#             {'public_id': user.public_id,
#              'exp':
#              datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
#             current_app.config['SECRET_KEY'])
#         # print(type(token))
#         return jsonify({'token': token})

#     return make_response(
#         'Could not verify', 401, {
#             'WWW-Authentication': "Basic realm='login req'"})
