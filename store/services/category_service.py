from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

from store.models.base.base_model import BaseSchema
from store.models.category.category_db import Category
from store.models.category.category_model import CategoryCreate, CategoryUpdate, CategoryCreateResponse, CategoryUpdateResponse, CategoryResponse, CategorysResponse, TopBooksSchema

class CategoryService:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.collection = db.category
        self.book_collection = db.book
        self.author_collection = db.author
        self.user_collection = db.user
        self.review_collection = db.review

    async def retrieve_categories(self) -> list[CategorysResponse]:
        result = self.collection.find()

        categories = []
        async for category in result:
            category = self.__replace_id(category)

            categories.append(CategoryResponse(**category))
        return categories
    
    async def create_category(self, category: CategoryCreate) -> CategoryCreateResponse:
        # Check if category name already exists
        existing = await self.collection.find_one({"name": category.name})
        if existing:
            raise HTTPException(status_code=400, detail="Category with this name already exists")
        
        category_dict = category.model_dump()
        category_dict["book_count"] = 0
        
        category_obj = Category(**category_dict)
        result = await self.collection.insert_one(category_obj.model_dump())
        
        return await self.retrieve_category(str(result.inserted_id))
    
    async def retrieve_category(self, category_id: str) -> CategoryResponse:
        try:
            object_id = ObjectId(category_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid category ID format")
            
        category = await self.collection.find_one({"_id": object_id})
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        category = self.__replace_id(category)
        
        # Get top books for this category
        top_books = []
        pipeline = [
            {"$match": {"categories": {"$elemMatch": {"$eq": object_id}}}},
            {"$sort": {"average_rating": -1}},
            {"$limit": 5}
        ]
        
        cursor = self.book_collection.aggregate(pipeline)
        async for book in cursor:
            book = self.__replace_id(book)
            book_id = str(book["_id"])
            book_title = book["title"]
            author_id = str(book.get("author_id", ""))
            avg_rating = book.get("average_rating", 0)
            
            # Get author info
            author = None
            if author_id:
                author_doc = await self.author_collection.find_one({"_id": ObjectId(author_id)})
                if author_doc:
                    author = BaseSchema(id=str(author_doc["_id"]), name=author_doc["name"])
            
            top_books.append(
                TopBooksSchema(
                    id=book_id,
                    title=book_title,
                    author=author,
                    average_rating=avg_rating
                ))
            print(top_books)
        
        category["top_books"] = top_books
        return CategoryResponse(**category)

    async def update_category(self, category_id: str, category: CategoryUpdate) -> CategoryUpdateResponse:
        try:
            object_id = ObjectId(category_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid category ID format")
            
        # Check if category exists
        existing = await self.collection.find_one({"_id": object_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Check if name is being updated and if it already exists
        update_data = category.model_dump(exclude_unset=True)
        if "name" in update_data:
            name_exists = await self.collection.find_one({
                "name": update_data["name"],
                "_id": {"$ne": object_id}
            })
            if name_exists:
                raise HTTPException(status_code=400, detail="Category with this name already exists")

        # Update timestamp
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        await self.collection.update_one({"_id": object_id}, {"$set": update_data})
 
        return await self.retrieve_category(category_id)

    @staticmethod
    def __replace_id(document):
        document["id"] = str(document.pop("_id"))
        return document