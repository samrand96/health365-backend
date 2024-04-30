import copy, uuid, jwt
from datetime import datetime
from app.database.models.user import User, User_Pydantic, UserToken
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from tortoise import timezone
from app.helpers.constant import SECRET_KEY, ALGORITHM


async def validate_token(reset_token):
    user_token = await UserToken.get(token=reset_token)
    if user_token is not None:
        user_id = copy.deepcopy(user_token.user_id)
        diff = datetime.now() - timezone.make_naive(user_token.created_at, timezone=None)
        if diff.total_seconds() < 300:
            await UserToken.filter(token=reset_token).delete()
            return {'status_code': 200, 'user': user_id}
        await UserToken.filter(token=reset_token).delete()
        return JSONResponse(status_code=404, content="Token Expired")
    return JSONResponse(status_code=404, content="Invalid Token")


async def create_verification_token(user):
    user_token_obj = await UserToken(token=uuid.uuid4())
    user_token_obj.created_at = datetime.now()
    user_token_obj.user = user
    await user_token_obj.save()
    return await user_token_obj


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def authenticate_user(username: str, password: str):
    user = await User.get(email=username)
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password'
        )

    return await User_Pydantic.from_tortoise_orm(user)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token has expired")
    except jwt.JWTError as e:
        raise HTTPException(status_code=403, detail=str(e))


def has_permission(required_roles: list):
    def role_checker(token: str = Depends(oauth2_scheme)):
        payload = verify_token(token)
        user_role =payload.get('role')
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        is_admin: bool = True if role == 'admin' else False
        if user_role not in required_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return {"id": user_id, "role": role, "is_admin": is_admin, "token_payload": payload}

    return role_checker
