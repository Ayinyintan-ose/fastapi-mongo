from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="env/.env")
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(MONGO_URI)

try:
    client.admin.command('ping')
    print("Connected successfully!")
except Exception as e:
    print("MongoDB connection failed:", e)

db = client["doc_management"]

user_collection = db["users"]
document_collection = db["documents"]
