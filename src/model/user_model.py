from typing import List
from pydantic import BaseModel, EmailStr

from src.model.book_model import BookSchema


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    books: List[BookSchema] = []

    class Config:
        json_schema_extra = {
            "example": {
                "username": "John Doe",
                "email": "jdoe@x.edu.ng",
                "password": "jyekk@1726JY278",
                "books": []
            }
        }


class UserLoginSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "John Doe",
                "email": "jdoe@x.edu.ng",
                "password": "jyekk@1726JY278",
            }
        }


def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "books": user["books"],
        "book_count": len(user["books"])
    }


def response_model(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }


def error_response_model(error, code, message):
    return {"error": error, "code": code, "message": message}
