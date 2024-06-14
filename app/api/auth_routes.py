from flask import Blueprint, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models import db, Profile
import pyotp
from app import oauth

auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = generate_password_hash(data.get('password'))
    fullName = data.get('fullName')

    if not all([username, email, password, fullName]):
        return jsonify({"message": "All fields are required"}), 400

    new_user = Profile(username=username, email=email, password=password, fullName=fullName)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error registering user"}), 500

@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing fields"}), 400

    user = Profile.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify(jwt_token=access_token), 200
    return jsonify({"error": "Invalid credentials"}), 401

@auth_routes.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"message": "Logged out successfully"}), 200

@auth_routes.route('/current_user', methods=['GET'])
@jwt_required()
def current_user_info():
    user_id = get_jwt_identity()
    user = Profile.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "username": user.username,
        "email": user.email,
        "fullName": user.fullName,
        "avatar": user.avatar,
        "active": user.active,
        "createdAt": user.createdAt,
        "updatedAt": user.updatedAt
    }), 200

@auth_routes.route('/2fa-setup', methods=['POST'])
@jwt_required()
def setup_2fa():
    user_id = get_jwt_identity()
    user = Profile.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    totp = pyotp.TOTP(user.email).provisioning_uri(name=user.email, issuer_name="Stonks")
    return jsonify({"otp_url": totp}), 200

@auth_routes.route('/2fa-verify', methods=['POST'])
@jwt_required()
def verify_2fa():
    data = request.get_json()
    otp = data.get('otp')
    user_id = get_jwt_identity()
    user = Profile.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    totp = pyotp.TOTP(user.email)
    if totp.verify(otp):
        user.is_2fa_enabled = True
        db.session.commit()
        return jsonify({"message": "2FA enabled successfully"}), 200
    return jsonify({"message": "Invalid OTP"}), 400

@auth_routes.route('/login/google')
def google_login():
    redirect_uri = url_for('auth.google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_routes.route('/google/auth')
def google_auth():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.parse_id_token(token)
    user = Profile.query.filter_by(email=user_info['email']).first()

    if user is None:
        user = Profile(
            username=user_info['name'],
            email=user_info['email'],
            fullName=user_info['name']
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    access_token = create_access_token(identity=user.id)
    return jsonify(jwt_token=access_token), 200

# Error handler for KeyError during session teardown
@auth_routes.errorhandler(KeyError)
def handle_key_error(error):
    if 'session' in str(error):
        return '', 200
    else:
        return jsonify({"message": "An error occurred"}), 500
