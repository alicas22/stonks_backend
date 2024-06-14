from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from ..models import db, Profile, Channel, Role
from ..utils import send_email, send_push_notification
from flask_socketio import emit


channel_routes = Blueprint('channels', __name__)


@channel_routes.route('/<id>/livechat', methods=['POST'])
@login_required
def livechat(id):
    data = request.get_json()
    channel = Channel.query.get(id)
    if not channel:
        return jsonify({"message": "Channel not found"}), 404
    message = data['message']
    # socketio.emit('chat_message', {'message': message, 'channel_id': id}, broadcast=True)
    return jsonify({"message": "Message sent"}), 200

@channel_routes.route('/', methods=['POST'])
@login_required
def create_channel():
    data = request.get_json()
    new_channel = Channel(
        title=data['title'],
        description=data['description'],
        host_id=current_user.id
    )
    db.session.add(new_channel)
    db.session.commit()
    return jsonify({"message": "Channel created successfully"}), 201

@channel_routes.route('/<id>/set_admin', methods=['POST'])
@login_required
def set_admin(id):
    data = request.get_json()
    channel = Channel.query.get(id)
    if not channel or channel.host_id != current_user.id:
        return jsonify({"message": "Unauthorized or channel not found"}), 403
    user_id = data['user_id']
    user = Profile.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    role = Role.query.filter_by(profile_id=user_id, channel_id=id).first()
    if role:
        role.name = 'ADMIN'
    else:
        new_role = Role(name='ADMIN', profile_id=user_id, channel_id=id)
        db.session.add(new_role)
    db.session.commit()
    return jsonify({"message": "User set as admin"}), 200

@channel_routes.route('/<id>/unset_admin', methods=['POST'])
@login_required
def unset_admin(id):
    data = request.get_json()
    channel = Channel.query.get(id)
    if not channel or channel.host_id != current_user.id:
        return jsonify({"message": "Unauthorized or channel not found"}), 403
    user_id = data['user_id']
    role = Role.query.filter_by(profile_id=user_id, channel_id=id).first()
    if role and role.name == 'ADMIN':
        db.session.delete(role)
        db.session.commit()
        return jsonify({"message": "User unset as admin"}), 200
    return jsonify({"message": "User is not an admin"}), 404

@channel_routes.route('/<id>/mute', methods=['POST'])
@login_required
def mute_user(id):
    data = request.get_json()
    channel = Channel.query.get(id)
    if not channel:
        return jsonify({"message": "Channel not found"}), 404
    if not (current_user.id == channel.host_id or Role.query.filter_by(profile_id=current_user.id, channel_id=id, name='ADMIN').first()):
        return jsonify({"message": "Unauthorized"}), 403
    user_id = data['user_id']
    user = Profile.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    user.muted_channels.append(channel)
    db.session.commit()
    return jsonify({"message": f"User {user.username} muted"}), 200

@channel_routes.route('/<id>/unmute', methods=['POST'])
@login_required
def unmute_user(id):
    data = request.get_json()
    channel = Channel.query.get(id)
    if not channel:
        return jsonify({"message": "Channel not found"}), 404
    if not (current_user.id == channel.host_id or Role.query.filter_by(profile_id=current_user.id, channel_id=id, name='ADMIN').first()):
        return jsonify({"message": "Unauthorized"}), 403
    user_id = data['user_id']
    user = Profile.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    user.muted_channels.remove(channel)
    db.session.commit()
    return jsonify({"message": f"User {user.username} unmuted"}), 200

@channel_routes.route('/<id>/ban', methods=['POST'])
@login_required
def ban_user(id):
    data = request.get_json()
    channel = Channel.query.get(id)
    if not channel:
        return jsonify({"message": "Channel not found"}), 404
    if not (current_user.id == channel.host_id or Role.query.filter_by(profile_id=current_user.id, channel_id=id, name='ADMIN').first()):
        return jsonify({"message": "Unauthorized"}), 403
    user_id = data['user_id']
    user = Profile.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    user.banned_channels.append(channel)
    db.session.commit()
    return jsonify({"message": f"User {user.username} banned"}), 200

@channel_routes.route('/<id>/unban', methods=['POST'])
@login_required
def unban_user(id):
    data = request.get_json()
    channel = Channel.query.get(id)
    if not channel:
        return jsonify({"message": "Channel not found"}), 404
    if not (current_user.id == channel.host_id or Role.query.filter_by(profile_id=current_user.id, channel_id=id, name='ADMIN').first()):
        return jsonify({"message": "Unauthorized"}), 403
    user_id = data['user_id']
    user = Profile.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    user.banned_channels.remove(channel)
    db.session.commit()
    return jsonify({"message": f"User {user.username} unbanned"}), 200

@channel_routes.route('/<id>/suspend', methods=['POST'])
@login_required
def suspend_channel(id):
    channel = Channel.query.get(id)
    if not channel:
        return jsonify({"message": "Channel not found"}), 404
    if not current_user.is_superadmin:
        return jsonify({"message": "Unauthorized"}), 403
    channel.suspended = True
    db.session.commit()
    return jsonify({"message": "Channel suspended"}), 200

@channel_routes.route('/<id>/set_title', methods=['POST'])
@login_required
def set_title(id):
    data = request.get_json()
    channel = Channel.query.get(id)
    if not channel or channel.host_id != current_user.id:
        return jsonify({"message": "Unauthorized or channel not found"}), 403
    channel.title = data['title']
    db.session.commit()
    return jsonify({"message": "Channel title updated"}), 200

@channel_routes.route('/<id>/set_description', methods=['POST'])
@login_required
def set_description(id):
    data = request.get_json()
    channel = Channel.query.get(id)
    if not channel or channel.host_id != current_user.id:
        return jsonify({"message": "Unauthorized or channel not found"}), 403
    channel.description = data['description']
    db.session.commit()
    return jsonify({"message": "Channel description updated"}), 200
