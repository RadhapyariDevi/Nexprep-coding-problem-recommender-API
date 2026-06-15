# database.py
import os
from pymongo import MongoClient
import certifi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "algo_recommendation_db")

# 2. Establish connection with explicit timeout controls so it doesn't hang
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000,tlsCAFile=certifi.where())
db = client[DB_NAME]

problems_collection = db["cf_problems"]

try:
    client.admin.command('ping')
    print("[database] Successfully authenticated and connected to MongoDB Atlas Cloud!")
except Exception as e:
    print(f"[database CRITICAL] Could not connect to Atlas. Check your password/IP settings. Error: {e}")

# Build index for optimal sorting paths
problems_collection.create_index("cf_rating")
