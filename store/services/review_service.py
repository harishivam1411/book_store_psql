from fastapi import HTTPException
from bson import ObjectId
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

from store.models.review.review_db import Review
from store.models.review.review_model import ReviewCreate, ReviewUpdate, ReviewCreateResponse, ReviewUpdateResponse, ReviewResponse, ReviewsResponse

class ReviewService:
    def __init__(self, db : AsyncIOMotorClient):
        self.db = db
        self.collection = db.review
        self.book_collection = db.book
        self.author_collection = db.author
        self.user_collection = db.user
        self.category_collection = db.category

    async def retrieve_reviews(self, book_id: str) -> list[ReviewsResponse]:
    
        book = await self.book_collection.find_one({'_id': ObjectId(book_id)})
        if not book:
            raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")
        
        result = self.collection.find({"book_id": book_id})
        reviews = []
        async for review in result:
            review_copy = review.copy()  
            review_copy = self.__replace_id(review_copy)
            
            if "user_id" in review_copy and not review_copy.get("user"):
                try:
                    user = await self.user_collection.find_one({"_id": ObjectId(review_copy["user_id"])})
                except:
                    user = await self.user_collection.find_one({"_id": review_copy["user_id"]})
                
                if user:
                    user = self.__replace_id(user)
                    review_copy["user"] = {
                        "id": user["id"],
                        "username": user.get("username", "")
                    }
                else:
                    review_copy["user"] = {
                        "id": review_copy["user_id"],
                        "username": "Unknown user"
                    }
            
            reviews.append(ReviewsResponse(**review_copy))
        return reviews

    async def create_review(self, book_id: str, user_id: str, review_create: ReviewCreate) -> ReviewCreateResponse:
       
        book = await self.book_collection.find_one({"_id": ObjectId(book_id)})
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

       
        try:
            user = await self.user_collection.find_one({"_id": ObjectId(user_id)})
        except:
            user = await self.user_collection.find_one({"_id": user_id})

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        user = self.__replace_id(user)

        
        existing_review = await self.collection.find_one({
            "book_id": book_id,
            "user_id": user_id
        })
        if existing_review:
            raise HTTPException(status_code=400, detail="User has already reviewed this book")

       
        review_dict = review_create.model_dump()
        review_dict["book_id"] = book_id
        review_dict["user_id"] = user_id
        review_dict["user"] = {
            "id": user_id,
            "username": user.get("username", "Unknown user"),
            "first_name": user.get("first_name", ""),
            "last_name": user.get("last_name", "")
        }
        review_dict["created_at"] = datetime.now(timezone.utc)
        review_dict["updated_at"] = datetime.now(timezone.utc)

        
        review = Review(**review_dict)
        result = await self.collection.insert_one(review.model_dump())

        
        user_id_obj = ObjectId(user_id) if not isinstance(user["id"], ObjectId) else user["id"]
        await self.user_collection.update_one(
            {"_id": user_id_obj},
            {
                "$inc": {"review_count": 1},
                "$push": {
                    "recent_reviews": {
                        "id": str(result.inserted_id),
                        "book": {"id": book_id, "title": book["title"]},
                        "rating": review_dict["rating"],
                        "created_at": datetime.now(timezone.utc)
                    }
                }
            }
        )

       
        book_reviews = self.collection.find({"book_id": book_id})
        total_rating = count = 0
        async for r in book_reviews:
            total_rating += r["rating"]
            count += 1

        if count > 0:
            avg_rating = total_rating / count
            await self.book_collection.update_one(
                {"_id": ObjectId(book_id)},
                {"$set": {"average_rating": avg_rating}}
            )

     
        inserted_review = await self.collection.find_one({"_id": result.inserted_id})
        inserted_review = self.__replace_id(inserted_review)
        
       
        if "user" not in inserted_review or not isinstance(inserted_review["user"], dict):
            inserted_review["user"] = review_dict["user"]

        return ReviewCreateResponse(**inserted_review)

    async def retrieve_review(self, book_id: str, review_id: str) -> ReviewResponse:
        try:
        
            review_obj_id = ObjectId(review_id)
            
          
            review = await self.collection.find_one({
                "_id": review_obj_id,
                "book_id": book_id
            })
            
            if not review:
                raise HTTPException(status_code=404, detail="Review not found")
            
           
            review = self.__replace_id(review)
                
         
            user_id = review.get("user_id")
            if user_id:
                try:
                    user = await self.user_collection.find_one({"_id": ObjectId(user_id)})
                except:
                    user = await self.user_collection.find_one({"_id": user_id})
                    
                if user:
                    user = self.__replace_id(user)
                    review["user"] = {
                        "id": user["id"],
                        "username": user.get("username", "Unknown user"),
                        "first_name": user.get("first_name", ""),
                        "last_name": user.get("last_name", "")
                    }
                else:
                
                    review["user"] = {
                        "id": user_id,
                        "username": "Unknown user",
                        "first_name": "",
                        "last_name": ""
                    }
            
            elif "user" in review and isinstance(review["user"], dict):
                user_dict = review["user"]
                if "first_name" not in user_dict or "last_name" not in user_dict:
                    try:
                        user = await self.user_collection.find_one({"_id": ObjectId(user_dict["id"])})
                    except:
                        user = await self.user_collection.find_one({"_id": user_dict["id"]})
                        
                    if user:
                        user = self.__replace_id(user)
                        review["user"] = {
                            "id": user_dict["id"],
                            "username": user_dict.get("username", user.get("username", "Unknown user")),
                            "first_name": user.get("first_name", ""),
                            "last_name": user.get("last_name", "")
                        }
                    else:
                     
                        review["user"]["first_name"] = review["user"].get("first_name", "")
                        review["user"]["last_name"] = review["user"].get("last_name", "")
            else:
              
                review["user"] = {
                    "id": "unknown",
                    "username": "Unknown user",
                    "first_name": "",
                    "last_name": ""
                }
                
            return ReviewResponse(**review)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving review: {str(e)}")

    async def update_review(self, book_id: str, review_id: str, user_id: str, review_update: ReviewUpdate) -> ReviewUpdateResponse:
        try:
       
            review = await self.collection.find_one({
                "_id": ObjectId(review_id),
                "book_id": book_id
            })
            
            if not review:
                raise HTTPException(status_code=404, detail="Review not found")
            
       
            review_user_id = str(review.get("user_id", ""))
            if not review_user_id or review_user_id != str(user_id):
                if "user" in review and isinstance(review["user"], dict):
                    if str(review["user"].get("id", "")) != str(user_id):
                        raise HTTPException(status_code=403, detail="Not authorized to update this review")
                else:
                    raise HTTPException(status_code=403, detail="Not authorized to update this review")
                
         
            update_data = review_update.model_dump(exclude_unset=True)
            if not update_data:
                raise HTTPException(status_code=400, detail="No fields to update")
                
         
            update_data["updated_at"] = datetime.now(timezone.utc)
            
        
            await self.collection.update_one(
                {"_id": ObjectId(review_id)},
                {"$set": update_data}
            )
            
           
            if "rating" in update_data:
                book_reviews = self.collection.find({"book_id": book_id})
                total_rating = 0
                count = 0
                
                async for r in book_reviews:
                    total_rating += r["rating"]
                    count += 1
                    
                if count > 0:
                    avg_rating = total_rating / count
                    await self.book_collection.update_one(
                        {"_id": ObjectId(book_id)},
                        {"$set": {"average_rating": avg_rating}}
                    )
            
          
            updated_review = await self.collection.find_one({"_id": ObjectId(review_id)})
            updated_review = self.__replace_id(updated_review)
            
           
            try:
                user = await self.user_collection.find_one({"_id": ObjectId(user_id)})
            except:
                user = await self.user_collection.find_one({"_id": user_id})
                
            if user:
                user = self.__replace_id(user)
                updated_review["user"] = {
                    "id": user_id,
                    "username": user.get("username", "Unknown user"),
                    "first_name": user.get("first_name", ""),
                    "last_name": user.get("last_name", "")
                }
            else:
              
                updated_review["user"] = {
                    "id": user_id,
                    "username": "Unknown user",
                    "first_name": "",
                    "last_name": ""
                }
                
            return ReviewResponse(**updated_review)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating review: {str(e)}")
    
    @staticmethod
    def __replace_id(document):
        if document and '_id' in document:
            document['id'] = str(document.pop('_id'))
        return document