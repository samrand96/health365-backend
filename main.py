import socketio
from fastapi import FastAPI
from app.database.database import init_db
from app.routers import users, utilities, patients

app = FastAPI()

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app_asgi = socketio.ASGIApp(sio, app=app)

app.include_router(users.router)
app.include_router(utilities.router)
app.include_router(patients.router)

app.mount('/', app_asgi)


@app.on_event("startup")
async def startup_event():
    """
        A function that handles the startup event by initializing the database.
        No parameters are required. Does not return anything.
    """
    print("INITIALISING DATABASE")
    init_db(app)
