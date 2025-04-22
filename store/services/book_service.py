from fastapi import HTTPException
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import UpdateOne

from store.models.book.book_db import Book
from store.models.book.book_model import BookCreate, BookUpdate, BookCreateResponse, BookUpdateResponse, BookResponse, BooksResponse

class BookService:
    def __init__(self, db : AsyncIOMotorClient):
        self.db = db
        self.collection = db.book
        self.author_collection = db.author
        self.user_collection = db.user
        self.review_collection = db.review
        self.category_collection = db.category

    async def retrieve_books(self) -> list[BooksResponse]:
        result = self.collection.find()
        books = []
        async for book in result:
            book = self.__replace_id(book)
            
            # Fetch author details
            if book.get("author_id"):
                author = await self.author_collection.find_one({"_id": ObjectId(book["author_id"])})
                if author:
                    author = self.__replace_id(author)
                    book["author"] = {"id": author["id"], "name": author["name"]}
                else:
                    book["author"] = {"id": book["author_id"], "name": "Unknown Author"}
            else:
                book["author"] = {"id": "", "name": "Unknown Author"}
            
            # Fetch category details
            categories = []
            if book.get("category_ids"):
                for cat_id in book["category_ids"]:
                    try:
                        category = await self.category_collection.find_one({"_id": ObjectId(cat_id)})
                        if category:
                            category = self.__replace_id(category)
                            categories.append({"id": category["id"], "name": category["name"]})
                    except:
                        pass
            
            book["categories"] = categories
            
            # Calculate average rating if available
            if book_id := book.get("id"):
                avg_rating = await self.__calculate_avg_rating(book_id)
                book["average_rating"] = avg_rating
            
            books.append(BookResponse(**book))
        return books

    async def create_book(self, book: BookCreate) -> BookCreateResponse:
        book_dict = book.model_dump()

        # Validate author exists
        if not await self.__author_exists(book.author_id):
            raise HTTPException(status_code=400, detail={
                "error": "Bad Request",
                "message": "Invalid input data",
                "details": {
                    "author_id": [f"Author with ID {book.author_id} does not exist"]
                }
            })
        
        # Validate categories exist
        invalid_categories = await self.__validate_categories(book.category_ids)
        if invalid_categories:
            raise HTTPException(status_code=400, detail={
                "error": "Bad Request",
                "message": "Invalid input data",
                "details": {
                    "category_ids": [f"Category with ID {cat_id} does not exist" for cat_id in invalid_categories]
                }
            })

        # Get author details
        author = await self.__get_author(book.author_id)
        book_dict['author'] = author
        
        # Get category details
        categories = await self.__get_categories(book.category_ids)
        book_dict['categories'] = categories
        
        category_ids = [ObjectId(category_id) for category_id in book_dict["category_ids"]]
        if category_ids:
            updates = [
            UpdateOne({"_id": ObjectId(category_id)}, {"$inc": {"book_count": 1}})
            for category_id in category_ids]

        author_id = ObjectId(book_dict["author_id"])
        if author_id:
            await self.author_collection.update_one(
            {"_id": author_id},
            {"$inc": {"book_count": 1}}
        )

        await self.category_collection.bulk_write(updates)

        # Create the book
        book_model = Book(**book_dict)
        result = await self.collection.insert_one(book_model.model_dump())
        
        return await self.retrieve_book(str(result.inserted_id))

    async def retrieve_book(self, book_id: str) -> BookResponse:
        try:
            book = await self.collection.find_one({'_id': ObjectId(book_id)})
            if not book:
                raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")
                
            book = self.__replace_id(book)
            
            # Get author details if not present
            if not book.get("author") and book.get("author_id"):
                author = await self.__get_author(book["author_id"])
                book["author"] = author
            
            # Get categories if not present
            if not book.get("categories") and book.get("category_ids"):
                categories = await self.__get_categories(book["category_ids"])
                book["categories"] = categories
            
            # Calculate average rating
            book["average_rating"] = await self.__calculate_avg_rating(book_id)
            
            return BookResponse(**book)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")

    async def update_book(self, book_id: str, book: BookUpdate) -> BookUpdateResponse:
        # Verify book exists
        existing_book = await self.collection.find_one({'_id': ObjectId(book_id)})
        if not existing_book:
            raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")
        
        update_data = book.model_dump(exclude_unset=True)

        # Validate author if being updated
        if author_id := update_data.get("author_id"):
            if not await self.__author_exists(author_id):
                raise HTTPException(status_code=400, detail={
                    "error": "Bad Request",
                    "message": "Invalid input data",
                    "details": {
                        "author_id": [f"Author with ID {author_id} does not exist"]
                    }
                })
        
        # Validate categories if being updated
        if category_ids := update_data.get("category_ids"):
            invalid_categories = await self.__validate_categories(category_ids)
            if invalid_categories:
                raise HTTPException(status_code=400, detail={
                    "error": "Bad Request", 
                    "message": "Invalid input data",
                    "details": {
                        "category_ids": [f"Category with ID {cat_id} does not exist" for cat_id in invalid_categories]
                    }
                })

        # Get author details
        author = await self.__get_author(book.author_id)
        update_data['author'] = author
        
        # Get category details
        categories = await self.__get_categories(book.category_ids)
        update_data['categories'] = categories
        
        # Update the 'updated_at' timestamp
        from datetime import datetime, timezone
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        await self.collection.update_one({'_id': ObjectId(book_id)}, {'$set': update_data})
        
        return await self.retrieve_book(book_id)
    
    async def __author_exists(self, author_id: str) -> bool:
        try:
            author = await self.author_collection.find_one({'_id': ObjectId(author_id)})
            return author is not None
        except:
            return False

    async def __validate_categories(self, category_ids: list[str]) -> list[str]:
        invalid_ids = []
        for cat_id in category_ids:
            try:
                category = await self.category_collection.find_one({'_id': ObjectId(cat_id)})
                if not category:
                    invalid_ids.append(cat_id)
            except:
                invalid_ids.append(cat_id)
        return invalid_ids

    async def __get_author(self, author_id: str) -> dict:
        try:
            author = await self.author_collection.find_one({'_id': ObjectId(author_id)})
            if not author:
                return {"id": author_id, "name": "Unknown Author"}
            
            author = self.__replace_id(author)
            return {"id": author["id"], "name": author["name"]}
        except:
            return {"id": author_id, "name": "Unknown Author"}

    async def __get_categories(self, category_ids: list[str]) -> list[dict]:
        categories = []
        for cat_id in category_ids:
            try:
                category = await self.category_collection.find_one({'_id': ObjectId(cat_id)})
                if category:
                    category = self.__replace_id(category)
                    categories.append({"id": category["id"], "name": category["name"]})
            except:
                pass
        return categories

    async def __calculate_avg_rating(self, book_id: str) -> float:
        try:
            pipeline = [
                {"$match": {"book_id": book_id}},
                {"$group": {"_id": None, "avgRating": {"$avg": "$rating"}}}
            ]
            result = await self.review_collection.aggregate(pipeline).to_list(length=1)
            if result and len(result) > 0:
                return round(result[0]["avgRating"], 1)
            return 0
        except:
            return 0

    @staticmethod
    def __replace_id(document):
        if document:
            document['id'] = str(document.pop('_id'))
        return document
