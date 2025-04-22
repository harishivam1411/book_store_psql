from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient

from store.database import get_database
from store.utils.dependencies import get_current_user
from store.models.auth.auth_model import TokenPayload
from store.services.author_service import AuthorService
from store.models.author.author_model import AuthorCreate, AuthorUpdate, AuthorCreateResponse, AuthorUpdateResponse, AuthorResponse, AuthorsResponse

author_router = APIRouter(prefix='/authors', tags=['Authors'])

@author_router.get('/', response_model=list[AuthorsResponse])
async def retrieve_authors(db: AsyncIOMotorClient = Depends(get_database)):
    service = AuthorService(db)
    return await service.retrieve_authors()

@author_router.post('/', response_model=AuthorCreateResponse)
async def create_author(author: AuthorCreate, db: AsyncIOMotorClient = Depends(get_database)):
    service = AuthorService(db)
    return await service.create_author(author)

@author_router.get('/{author_id}', response_model=AuthorResponse)
async def retrieve_author(author_id: str, db: AsyncIOMotorClient = Depends(get_database)):
    service = AuthorService(db)
    return await service.retrieve_author(author_id)

@author_router.put('/{author_id}', response_model=AuthorUpdateResponse)
async def update_author(author_id: str, author: AuthorUpdate, db: AsyncIOMotorClient = Depends(get_database)):
    service = AuthorService(db)
    return await service.update_author(author_id, author)