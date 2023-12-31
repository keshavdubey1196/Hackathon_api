from datetime import datetime
from app import db


# Association table for MtoM rel bw hackathon and users
user_hackathons = db.Table('user_hackathons',
                           db.Column("id", db.Integer(), primary_key=True,
                                     autoincrement=True),
                           db.Column('user_id', db.Integer(), db.ForeignKey(
                               'users.id'), primary_key=True),
                           db.Column(
                               'hackathon_id', db.Integer(),
                               db.ForeignKey('hackathons.id'),
                               primary_key=True))


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    public_id = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), unique=True, nullable=False)
    created_at = db.Column(
        db.DateTime(), default=datetime.utcnow)
    is_admin = db.Column(db.Boolean(), default=False, nullable=False)

    created_hackathons = db.relationship(
        'Hackathon', backref='creator', lazy=True,
        cascade='all, delete-orphan')

    participated_hackathons = db.relationship(
        'Hackathon', secondary=user_hackathons,
        backref='participants', lazy=True)


class Hackathon(db.Model):
    __tablename__ = 'hackathons'

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    bg_image = db.Column(db.String(200), nullable=True)
    hakthon_img = db.Column(db.String(200), nullable=True)
    submission_type = db.Column(db.String(10), nullable=False, default="File")
    rewards = db.Column(db.Integer(), nullable=True, default=500)
    created_at = db.Column(
        db.DateTime(), default=datetime.utcnow)
    start_datetime = db.Column(db.DateTime(), nullable=True)
    end_datetime = db.Column(db.DateTime(), nullable=True)
    submissions = db.relationship(
        'Submission', backref='hackathon', lazy=True,
        cascade='all, delete-orphan')
    creator_id = db.Column(db.String(200), db.ForeignKey('users.public_id'))


class Submission(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    file = db.Column(db.String(200), nullable=True)
    url = db.Column(db.String(300), nullable=True)
    created_at = db.Column(
        db.DateTime(), default=datetime.utcnow)
    user_id = db.Column(db.String(200), db.ForeignKey(
        'users.public_id'), nullable=False)
    hackathon_id = db.Column(db.Integer(), db.ForeignKey(
        'hackathons.id'), nullable=True)

    user = db.relationship('User', backref='submissions', lazy=True)
