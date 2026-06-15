# database.py
import os
from pymongo import MongoClient
import certifi

load_dotenv()
# # 1. Paste your Atlas connection string directly as the fallback string here:
# DEFAULT_ATLAS_URI = "mongodb+srv://tester:vishara123@cluster0.5kv6xf8.mongodb.net/?appName=Cluster0"

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "algo_recommendation_db")

# 2. Establish connection with explicit timeout controls so it doesn't hang
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000,tlsCAFile=certifi.where())
db = client[DB_NAME]

problems_collection = db["cf_problems"]

# This forces Python to test the connection immediately right here
try:
    client.admin.command('ping')
    print("[database] Successfully authenticated and connected to MongoDB Atlas Cloud!")
except Exception as e:
    print(f"[database CRITICAL] Could not connect to Atlas. Check your password/IP settings. Error: {e}")

# Build index for optimal sorting paths
problems_collection.create_index("cf_rating")