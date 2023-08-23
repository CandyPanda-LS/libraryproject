from typing import Optional
from pydantic import BaseModel


class BookSchema(BaseModel):
    title: str
    author: str
    publication_date: Optional[str] = None
    isbn: Optional[str] = None
    cover_image: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "The Alchemist",
                "author": "Paulo Coelho",
                "publication_date": "1988-04-25",
                "isbn": "978-0-06-112241-5",
                "cover_image": "https://images-na.ssl-images-amazon.com/images/I/41rczj6x+XL._SX331_BO1,204,203,200_.jpg",
            }
        }

def book_helper(book) -> dict:
    return {
        "id": str(book["_id"]),
        "title": book["title"],
        "author": book["author"],
        "publication_date": book["publication_date"],
        "isbn": book["isbn"],
        "cover_image": book["cover_image"],
    }

def response_model(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }


def error_response_model(error, code, message):
    return {"error": error, "code": code, "message": message}
