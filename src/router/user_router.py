from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
import jwt
import logging

from src.database import user_collection
from src.model.user_model import UserSchema, user_helper, UserLoginSchema

user_router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@user_router.get("/users", response_description="List all users", tags=["User"])
async def get_users():
    try:
        users = []
        async for user in user_collection.find():
            users.append(user_helper(user))
        return users
    except Exception as e:
        logger.error(f"An error occurred while fetching users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@user_router.post("/register", response_description="Add new user", tags=["User"])
async def create_user(user: UserSchema):
    try:
        existing_user_email = await user_collection.find_one({"email": user.email})

        if existing_user_email:
            raise HTTPException(status_code=400, detail="Email already registered")

        user_data = {
            "email": user.email,
            "username": user.username,
            "hashed_password": pwd_context.hash(user.password),
            "books": user.books if user.books else []
        }

        user_collection.insert_one(user_data)
        logger.info(f"User registered successfully: {user.username}")
        return {'username': str(user.username)}
    except HTTPException as he:
        logger.error(f"An error occurred while creating user: {he}")
        raise he
    except Exception as e:
        logger.error(f"An error occurred while registering user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@user_router.post("/login", response_description="Login user", tags=["User"])
async def login_user(user: UserLoginSchema):
    try:
        user_data = await user_collection.find_one({"username": user.username})
        if user_data:
            if pwd_context.verify(user.password, user_data["hashed_password"]):
                jwt_payload = {"username": user.username}
                jwt_token = jwt.encode(jwt_payload, "secret_key", algorithm="HS256")
                logger.info(f"User logged in successfully: {user.username}")
                return {'username': str(user.username), 'token': jwt_token}
            else:
                raise HTTPException(status_code=400, detail="Incorrect password")
        else:
            raise HTTPException(status_code=400, detail="Username does not exist")
    except Exception as e:
        logger.error(f"An error occurred while logging in user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@user_router.get("/user/{token}", response_description="Get user by token", tags=["User"])
async def get_user( token: str):
    try:
        username = jwt.decode(token, "secret_key", algorithms=["HS256"])["username"]
        user = await user_collection.find_one({"username": username})
        if user:
            return user_helper(user)
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except jwt.ExpiredSignatureError:
        logger.error("JWT token has expired")
        raise HTTPException(status_code=401, detail="JWT token has expired")
    except jwt.DecodeError:
        logger.error("JWT token is invalid")
        raise HTTPException(status_code=401, detail="Invalid JWT token")
    except Exception as e:
        logger.error(f"An error occurred while fetching user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
