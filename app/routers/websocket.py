from app.helpers.security import verify_token
from main import sio
from fastapi import HTTPException

# A dictionary to keep track of online users and their sessions
online_users = {}

@sio.event
async def connect(sid, environ):
    print("A user connected:", sid)
    # Optionally authenticate and store user session here
    # You can access the HTTP headers from `environ`
    token = environ.get('HTTP_AUTHORIZATION')
    if token:
        user_id = verify_token(token)  # Implement this function in your auth helpers
        if user_id:
            online_users[sid] = user_id
            await sio.emit('connection_status', {'data': 'Connected successfully'}, room=sid)
        else:
            await sio.disconnect(sid)
    else:
        await sio.disconnect(sid)

@sio.event
async def disconnect(sid):
    print("A user disconnected:", sid)
    if sid in online_users:
        del online_users[sid]

@sio.event
async def send_patient_info(sid, data):
    """
    A custom event to handle sending patient information to another doctor.
    Data could contain: {'recipient_id': int, 'patient_info': dict}
    """
    if sid in online_users:
        recipient_id = data['recipient_id']
        patient_info = data['patient_info']
        # Emit patient info to the recipient if online
        recipient_sid = get_sid_from_user_id(recipient_id)
        if recipient_sid:
            await sio.emit('new_patient_info', patient_info, room=recipient_sid)
        else:
            print(f"Recipient user {recipient_id} is not online.")
    else:
        print("Unauthorized attempt to send patient information.")

def get_sid_from_user_id(user_id):
    """
    Retrieve the Socket.IO session id (sid) for a given user id.
    """
    for sid, uid in online_users.items():
        if uid == user_id:
            return sid
    return None

