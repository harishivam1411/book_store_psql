from fastapi import HTTPException
from bson import ObjectId
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

from store.models.author.author_db import Author
from store.models.author.author_model import AuthorCreate, AuthorUpdate, AuthorCreateResponse, AuthorUpdateResponse, AuthorResponse, AuthorsResponse, AuthorBooksSchema

class AuthorService:
    def __init__(self, db : AsyncIOMotorClient):
        self.db = db
        self.collection = db.author
        self.book_collection = db.book
        self.user_collection = db.user
        self.review_collection = db.review
        self.category_collection = db.category

    async def retrieve_authors(self) -> list[AuthorsResponse]:
        result = self.collection.find()

        authors = []
        async for author in result:
            author = self.__replace_id(author)

            authors.append(AuthorsResponse(**author))
        return authors

    async def create_author(self, author: AuthorCreate) -> AuthorCreateResponse:
        author_dict = author.model_dump()

        # Set default values
        author_dict["book_count"] = 0

        author = Author(**author_dict)
        result = await self.collection.insert_one(author.model_dump())
        return await self.retrieve_author(str(result.inserted_id))

    async def retrieve_author(self, author_id: str) -> AuthorResponse:
        try:
            author = await self.collection.find_one({'_id': ObjectId(author_id)})
            if not author:
                raise HTTPException(status_code=404, detail=f"Author with ID {author_id} not found")
            author = self.__replace_id(author)
            
            # Get book details for this author
            books = []
            cursor = self.book_collection.find({"author_id": author_id})
            async for book in cursor:
                book = self.__replace_id(book)
                # books.append({
                #     "id": book["id"],
                #     "title": book["title"],
                #     "isbn": book.get("isbn", ""),
                #     "publication_date": book.get("publication_date", "")
                # })
                books.append(AuthorBooksSchema(**book))
            
            author["books"] = books
            
            return AuthorResponse(**author)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=404, detail=f"Author with ID {author_id} not found")
        

    async def update_author(self, author_id: str, author: AuthorUpdate) -> AuthorUpdateResponse:
        # Verify author exists
        existing_author = await self.collection.find_one({'_id': ObjectId(author_id)})
        if not existing_author:
            raise HTTPException(status_code=404, detail=f"Author with ID {author_id} not found")
        
        update_data = author.model_dump(exclude_unset=True)
        
        # Update the 'updated_at' timestamp
        update_data["updated_at"] = datetime.now(timezone.utc)

        await self.collection.update_one({'_id': ObjectId(author_id)}, {'$set': update_data})
        
        return await self.retrieve_author(author_id)

    @staticmethod
    def __replace_id(document):
        document['id'] = str(document.pop('_id'))
        return document