from flask_socketio import emit, join_room, leave_room
from . import socketio

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'msg': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']
    print(f'Received join request for room: {room} by user: {username}')
    join_room(room)
    emit('status', {'msg': f'{username} has entered the room.'}, room=room)

@socketio.on('message')
def handle_message(data):
    username = data['username']
    room = data['room']
    msg = data['msg']
    print(f'Received message from {username} in room {room}: {msg}')
    emit('message', {'msg': f'{username}: {msg}'}, room=room)

@socketio.on('set admin')
def handle_set_admin(data):
    room = data['room']
    user_id = data['user_id']
    current_user_id = data['current_user_id']
    # Add logic to set admin role
    print(f'Setting admin in room {room} for user {user_id} by {current_user_id}')
    emit('status', {'msg': f'User {user_id} has been set as admin.'}, room=room)

@socketio.on('unset admin')
def handle_unset_admin(data):
    room = data['room']
    user_id = data['user_id']
    current_user_id = data['current_user_id']
    # Add logic to unset admin role
    print(f'Unsetting admin in room {room} for user {user_id} by {current_user_id}')
    emit('status', {'msg': f'User {user_id} has been unset as admin.'}, room=room)

@socketio.on('mute')
def handle_mute(data):
    room = data['room']
    user_id = data['user_id']
    print(f'Muting user {user_id} in room {room}')
    emit('status', {'msg': f'User {user_id} has been muted.'}, room=room)

@socketio.on('unmute')
def handle_unmute(data):
    room = data['room']
    user_id = data['user_id']
    print(f'Unmuting user {user_id} in room {room}')
    emit('status', {'msg': f'User {user_id} has been unmuted.'}, room=room)

@socketio.on('ban')
def handle_ban(data):
    room = data['room']
    user_id = data['user_id']
    print(f'Banning user {user_id} in room {room}')
    emit('status', {'msg': f'User {user_id} has been banned.'}, room=room)

@socketio.on('unban')
def handle_unban(data):
    room = data['room']
    user_id = data['user_id']
    print(f'Unbanning user {user_id} in room {room}')
    emit('status', {'msg': f'User {user_id} has been unbanned.'}, room=room)
