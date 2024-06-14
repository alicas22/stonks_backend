import asyncio
import websockets
import json

async def test_socket():
    uri = "ws://localhost:5000/ws"
    async with websockets.connect(uri) as websocket:
        async def send_and_receive(message):
            print(f"Sending: {message}")
            await websocket.send(message)
            response = await websocket.recv()
            print(f"Received: {response}")

        join_message = json.dumps({
            "event": "join",
            "payload": {
                "username": "testuser",
                "room": "testroom"
            }
        })
        await send_and_receive(join_message)

        message = json.dumps({
            "event": "message",
            "payload": {
                "msg": "Hello, world!",
                "room": "testroom",
                "username": "testuser"
            }
        })
        await send_and_receive(message)

        set_admin_message = json.dumps({
            "event": "set admin",
            "payload": {
                "room": "testroom",
                "user_id": 1,
                "current_user_id": 1
            }
        })
        await send_and_receive(set_admin_message)

        unset_admin_message = json.dumps({
            "event": "unset admin",
            "payload": {
                "room": "testroom",
                "user_id": 1,
                "current_user_id": 1
            }
        })
        await send_and_receive(unset_admin_message)

        mute_message = json.dumps({
            "event": "mute",
            "payload": {
                "room": "testroom",
                "user_id": 1
            }
        })
        await send_and_receive(mute_message)

        unmute_message = json.dumps({
            "event": "unmute",
            "payload": {
                "room": "testroom",
                "user_id": 1
            }
        })
        await send_and_receive(unmute_message)

        ban_message = json.dumps({
            "event": "ban",
            "payload": {
                "room": "testroom",
                "user_id": 1
            }
        })
        await send_and_receive(ban_message)

        unban_message = json.dumps({
            "event": "unban",
            "payload": {
                "room": "testroom",
                "user_id": 1
            }
        })
        await send_and_receive(unban_message)

        set_title_message = json.dumps({
            "event": "set title",
            "payload": {
                "room": "testroom",
                "title": "New Title"
            }
        })
        await send_and_receive(set_title_message)

        set_description_message = json.dumps({
            "event": "set description",
            "payload": {
                "room": "testroom",
                "description": "New Description"
            }
        })
        await send_and_receive(set_description_message)

if __name__ == "__main__":
    asyncio.run(test_socket())
