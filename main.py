from fastapi import FastAPI
from routes import users, documents
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="env/.env")



app = FastAPI()

client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
app.include_router(users.router)
app.include_router(documents.router)
print("Mongo URI:", os.getenv("MONGO_URI"))

