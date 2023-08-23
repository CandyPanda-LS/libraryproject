from fastapi import FastAPI

from src.router.book_router import book_router
from src.router.user_router import user_router
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(book_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
