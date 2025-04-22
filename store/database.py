import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGO_URI = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')

def get_database() -> AsyncIOMotorClient: # type: ignore
    try:
        database = AsyncIOMotorClient(MONGO_URI)
        yield database['Book_Store']
    except Exception as e:
        raise e