from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Profile, UserStatus, Follow
from ..utils import send_email, send_push_notification
import logging

profile_routes = Blueprint('profiles', __name__)

@profile_routes.route('/', methods=['GET'])
@jwt_required()
def get_profiles():
    profiles = Profile.query.all()
    return jsonify([profile.id for profile in profiles]), 200

@profile_routes.route('/<id>', methods=['GET'])
@jwt_required()
def get_profile(id):
    profile = Profile.query.get(id)
    if profile is None:
        return jsonify({"message": "Profile not found"}), 404
    return jsonify({
        "id": profile.id,
        "fullName": profile.fullName,
        "username": profile.username,
        "email": profile.email,
        "avatar": profile.avatar,
        "active": profile.active,
        "createdAt": profile.createdAt,
        "updatedAt": profile.updatedAt
    }), 200

@profile_routes.route('/', methods=['POST'])
@jwt_required()
def create_profile():
    data = request.get_json()
    profile = Profile(
        fullName=data['fullName'],
        username=data['username'],
        email=data['email'],
        password=data['password'],
        avatar=data.get('avatar', ''),
        active=data.get('active', True)
    )
    db.session.add(profile)
    db.session.commit()
    return jsonify({"message": "Profile created successfully"}), 201

@profile_routes.route('/<id>', methods=['PUT'])
@jwt_required()
def update_profile(id):
    profile = Profile.query.get(id)
    if profile is None:
        return jsonify({"message": "Profile not found"}), 404
    data = request.get_json()
    profile.fullName = data.get('fullName', profile.fullName)
    profile.username = data.get('username', profile.username)
    profile.email = data.get('email', profile.email)
    profile.password = data.get('password', profile.password)
    profile.avatar = data.get('avatar', profile.avatar)
    profile.active = data.get('active', profile.active)
    db.session.commit()
    return jsonify({"message": "Profile updated successfully"}), 200

@profile_routes.route('/<id>', methods=['DELETE'])
@jwt_required()
def delete_profile(id):
    profile = Profile.query.get(id)
    if profile is None:
        return jsonify({"message": "Profile not found"}), 404
    db.session.delete(profile)
    db.session.commit()
    return jsonify({"message": "Profile deleted successfully"}), 200

@profile_routes.route('/<id>/follow', methods=['POST'])
@jwt_required()
def follow(id):
    user_id = get_jwt_identity()
    if user_id == id:
        return jsonify({"message": "You cannot follow yourself"}), 400
    user = Profile.query.get(id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    follow = Follow.query.filter_by(follower_id=user_id, followed_id=id).first()
    if follow:
        return jsonify({"message": "You are already following this user"}), 400

    new_follow = Follow(follower_id=user_id, followed_id=id)
    db.session.add(new_follow)
    db.session.commit()
    return jsonify({"message": f"You are now following {user.username}"}), 200

@profile_routes.route('/<id>/unfollow', methods=['POST'])
@jwt_required()
def unfollow(id):
    user_id = get_jwt_identity()
    if user_id == id:
        return jsonify({"message": "You cannot unfollow yourself"}), 400
    user = Profile.query.get(id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    follow = Follow.query.filter_by(follower_id=user_id, followed_id=id).first()
    if not follow:
        return jsonify({"message": "You are not following this user"}), 400

    db.session.delete(follow)
    db.session.commit()
    return jsonify({"message": f"You have unfollowed {user.username}"}), 200

@profile_routes.route('/<id>/start_stream', methods=['POST'])
@jwt_required()
def start_stream(id):
    user_id = get_jwt_identity()
    user = Profile.query.get(id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    followers = user.followers.all()
    online_tokens = []  # Store FCM tokens for online users
    offline_emails = []  # Store emails for offline users

    # Split online and offline
    for follower in followers:
        status = UserStatus.query.filter_by(profile_id=follower.id).first()
        if status and status.is_online:
            tokens = [token.token for token in follower.fcmtokens]
            online_tokens.extend(tokens)
        else:
            offline_emails.append(follower.email)

    # Push to online
    online_notifications = []
    if online_tokens:
        online_notifications = send_push_notification(online_tokens, "Stream started", f"{user.username} has started a stream.")

    # Email offline
    for email in offline_emails:
        send_email(email, "Stream started", f"{user.username} has started a stream.")

    return jsonify({
        "message": "Notifications sent to followers",
        "offline_emails": offline_emails,
        "online_notifications": online_notifications,
        "debug": {
            "followers_count": len(followers),
            "online_tokens": online_tokens,
            "offline_emails_count": len(offline_emails),
            "online_notifications_count": len(online_notifications)
        }
    }), 200
