from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_reset_token(self, expires_sec=1800):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt='password-reset-salt')

    @staticmethod
    def verify_reset_token(token):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt='password-reset-salt', max_age=1800)['user_id']
        except:
            return None
        return User.query.get(user_id)

class Primer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application = db.Column(db.String(100), nullable=False)
    pcr = db.Column(db.String(100), nullable=True)
    target = db.Column(db.String(100), nullable=True)
    oligos = db.Column(db.String(100), nullable=True)
    sequence = db.Column(db.String(255), nullable=True)
    box = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    reference = db.Column(db.String(255), nullable=True)
    comment = db.Column(db.Text, nullable=True)

# Association table for the many-to-many relationship between Primers and PrimerLists
primer_list_association = db.Table('primer_list_association',
    db.Column('primer_id', db.Integer, db.ForeignKey('primer.id')),
    db.Column('primer_list_id', db.Integer, db.ForeignKey('primer_list.id'))
)

class PrimerList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    visibility = db.Column(db.String(50), default="private")  # "private" or "public"
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Owner of the list
    primers = db.relationship("Primer", secondary=primer_list_association, backref=db.backref('lists', lazy='dynamic'))
