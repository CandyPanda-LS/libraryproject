import jwt
import logging
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from src.database import user_collection, book_collection
from src.model.book_model import BookSchema

book_router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@book_router.get("/book", tags=["Book"], response_description="Get all books ")
async def get_books():
    try:
        cursor = book_collection.find({})
        books = [BookSchema(**book) for book in await cursor.to_list(length=200)]
        return books
    except Exception as e:
        logger.error(f"Error while fetching books: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@book_router.get("/book/{book_title}", response_description="List a book by id", tags=["Book"])
async def get_book(book_title: str):
    try:
        book = await book_collection.find_one({"title": book_title})
        if book:
            return BookSchema(**book)
        else:
            raise HTTPException(status_code=404, detail=f"Book {book_title} not found")
    except Exception as e:
        logger.error(f"Error while fetching book {book_title}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@book_router.get("/books/{token}", tags=["Book"], response_description="List all books of user")
async def get_books(token: str):
    try:
        username = jwt.decode(token, "secret_key", algorithms=["HS256"])["username"]
        user = await user_collection.find_one({"username": username})
        if user:
            user_books = user.get("books", [])
            book_objects = []

            for book_id in user_books:
                book = await book_collection.find_one({"_id": ObjectId(book_id)})
                if book:
                    book_objects.append(BookSchema(**book))

            return book_objects
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.DecodeError:
        logger.error("Token decode error")
        raise HTTPException(status_code=401, detail="Token decode error")
    except Exception as e:
        logger.error(f"Error while fetching user books: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@book_router.post("/book/{token}", response_description="Add new book for user", tags=["Book"])
async def add_book(token: str, book: BookSchema):
    try:
        username = jwt.decode(token, "secret_key", algorithms=["HS256"])["username"]
        user = await user_collection.find_one({"username": username})

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        book_dict = book.model_dump()
        inserted_book = await book_collection.insert_one(book_dict)
        book_id = inserted_book.inserted_id

        user_books = user.get("books", [])
        user_books.append(str(book_id))

        await user_collection.update_one(
            {"username": username},
            {"$set": {"books": user_books}}
        )

        logger.info(f"Book with ID: {book_id} added to user {username}")
        return {"message": f"Book with ID: {book_id} added to user {username}"}
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.DecodeError:
        logger.error("Token decode error")
        raise HTTPException(status_code=401, detail="Token decode error")
    except Exception as e:
        logger.error(f"Error while adding book: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@book_router.put("/book/{book_title}", response_description="Update a book of user", tags=["Book"])
async def update_book(book_title: str, updated_book: BookSchema):
    try:
        existing_book = await book_collection.find_one({"title": book_title})
        if existing_book:
            updated_data = updated_book.model_dump()
            res = await book_collection.update_one({"title": book_title}, {"$set": updated_data})
            logger.info(f"Book with title: {book_title} updated")
            return {"message": f"Book with title: {book_title} updated"}
        else:
            raise HTTPException(status_code=404, detail="Book not found")
    except Exception as e:
        logger.error(f"Error while updating book {book_title}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@book_router.delete("/book/{book_title}", response_description="Delete a book of user", tags=["Book"])
async def delete_book(book_title: str):
    try:
        existing_book = await book_collection.find_one({"title": book_title})
        if existing_book:
            await book_collection.delete_one({"title": book_title})
            logger.info(f"Book {book_title} deleted successfully")
            return {"message": "Book deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Book not found")
    except Exception as e:
        logger.error(f"Error while deleting book {book_title}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


