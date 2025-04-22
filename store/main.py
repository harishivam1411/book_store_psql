from fastapi import FastAPI
import uvicorn

from store.routers.book_router import book_router
from store.routers.author_router import author_router
from store.routers.user_router import user_router
from store.routers.review_router import review_router
from store.routers.category_router import category_router
from store.routers.auth_router import auth_router

app = FastAPI()

app.include_router(book_router)
app.include_router(author_router)
app.include_router(user_router)
app.include_router(review_router)
app.include_router(category_router)
app.include_router(auth_router)

@app.get("/")
async def root():
    return "Book server is up and running"

if __name__ == "__main__":
    uvicorn.run("store.main:app", host="127.0.0.1", port=8000, reload=True)