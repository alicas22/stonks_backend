from flask_sock import Sock
import json
from .models import db, Profile, Channel, Role

channels = {}  # To store channel information like users, admins, etc.

def init_sockets(sock):
    @sock.route("/ws")
    def websocket(ws):
        print("Client connected")
        while True:
            data = ws.receive()
            if data is None:
                break
            print(f"Received data: {data}")
            handle_message(ws, data)
        print("Client disconnected")

    def handle_message(ws, data):
        try:
            event, payload = parse_message(data)
            if event == "join":
                handle_join(ws, payload)
            elif event == "message":
                handle_message_event(ws, payload)
            elif event == "set admin":
                handle_set_admin(ws, payload)
            elif event == "unset admin":
                handle_unset_admin(ws, payload)
            elif event == "mute":
                handle_mute(ws, payload)
            elif event == "unmute":
                handle_unmute(ws, payload)
            elif event == "ban":
                handle_ban(ws, payload)
            elif event == "unban":
                handle_unban(ws, payload)
            elif event == "set title":
                handle_set_title(ws, payload)
            elif event == "set description":
                handle_set_description(ws, payload)
            elif event == "suspend":
                handle_suspend(ws, payload)
            # Add more handlers as needed
        except Exception as e:
            print(f"Error handling message: {e}")

    def parse_message(data):
        try:
            message = json.loads(data)
            event = message.get("event")
            payload = message.get("payload", {})
            print(f"Parsed event: {event}")
            print(f"Parsed payload: {payload}")
            return event, payload
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e} for data: {data}")
            return None, None
        except Exception as e:
            print(f"Unexpected error: {e} for data: {data}")
            return None, None

    def handle_join(ws, payload):
        username = payload.get("username")
        room = payload.get("room")
        if room not in channels:
            channels[room] = {"users": [], "admins": []}
        channels[room]["users"].append(username)
        response = {"message": f"{username} has joined the room {room}"}
        print(f"Sending response: {response}")
        ws.send(json.dumps(response))

    def handle_message_event(ws, payload):
        username = payload.get("username")
        room = payload.get("room")
        message = payload.get("msg")
        response = {"message": f"{username}: {message}"}
        print(f"Sending response: {response}")
        ws.send(json.dumps(response))

    def handle_set_admin(ws, payload):
        room = payload.get("room")
        user_id = payload.get("user_id")
        current_user_id = payload.get("current_user_id")
        if not is_host(current_user_id, room):
            return ws.send(json.dumps({"message": "Unauthorized"}))
        channels[room]["admins"].append(user_id)
        response = {"message": f"User {user_id} has been set as admin in room {room}"}
        ws.send(json.dumps(response))

    def handle_unset_admin(ws, payload):
        room = payload.get("room")
        user_id = payload.get("user_id")
        current_user_id = payload.get("current_user_id")
        if not is_host(current_user_id, room):
            return ws.send(json.dumps({"message": "Unauthorized"}))
        channels[room]["admins"].remove(user_id)
        response = {"message": f"User {user_id} has been unset as admin in room {room}"}
        ws.send(json.dumps(response))

    def handle_mute(ws, payload):
        room = payload.get("room")
        user_id = payload.get("user_id")
        current_user_id = payload.get("current_user_id")
        if not is_admin(current_user_id, room) and not is_host(current_user_id, room):
            return ws.send(json.dumps({"message": "Unauthorized"}))
        response = {"message": f"User {user_id} has been muted in room {room}"}
        ws.send(json.dumps(response))

    def handle_unmute(ws, payload):
        room = payload.get("room")
        user_id = payload.get("user_id")
        current_user_id = payload.get("current_user_id")
        if not is_admin(current_user_id, room) and not is_host(current_user_id, room):
            return ws.send(json.dumps({"message": "Unauthorized"}))
        response = {"message": f"User {user_id} has been unmuted in room {room}"}
        ws.send(json.dumps(response))

    def handle_ban(ws, payload):
        room = payload.get("room")
        user_id = payload.get("user_id")
        current_user_id = payload.get("current_user_id")
        if not is_admin(current_user_id, room) and not is_host(current_user_id, room):
            return ws.send(json.dumps({"message": "Unauthorized"}))
        response = {"message": f"User {user_id} has been banned from room {room}"}
        ws.send(json.dumps(response))

    def handle_unban(ws, payload):
        room = payload.get("room")
        user_id = payload.get("user_id")
        current_user_id = payload.get("current_user_id")
        if not is_admin(current_user_id, room) and not is_host(current_user_id, room):
            return ws.send(json.dumps({"message": "Unauthorized"}))
        response = {"message": f"User {user_id} has been unbanned from room {room}"}
        ws.send(json.dumps(response))

    def handle_set_title(ws, payload):
        room = payload.get("room")
        title = payload.get("title")
        current_user_id = payload.get("current_user_id")
        if not is_host(current_user_id, room):
            return ws.send(json.dumps({"message": "Unauthorized"}))
        response = {"message": f"Title for room {room} has been set to {title}"}
        ws.send(json.dumps(response))

    def handle_set_description(ws, payload):
        room = payload.get("room")
        description = payload.get("description")
        current_user_id = payload.get("current_user_id")
        if not is_host(current_user_id, room):
            return ws.send(json.dumps({"message": "Unauthorized"}))
        response = {"message": f"Description for room {room} has been set to {description}"}
        ws.send(json.dumps(response))

    def handle_suspend(ws, payload):
        room = payload.get("room")
        current_user_id = payload.get("current_user_id")
        if not is_superadmin(current_user_id):
            return ws.send(json.dumps({"message": "Unauthorized"}))
        response = {"message": f"Channel {room} has been suspended"}
        ws.send(json.dumps(response))

    def is_host(user_id, room):
        channel = Channel.query.get(room)
        return channel and channel.host_id == user_id

    def is_admin(user_id, room):
        role = Role.query.filter_by(profile_id=user_id, channel_id=room, name='ADMIN').first()
        return role is not None

    def is_superadmin(user_id):
        user = Profile.query.get(user_id)
        return user and user.is_superadmin  # Assuming `is_superadmin` is a boolean field in `Profile`
