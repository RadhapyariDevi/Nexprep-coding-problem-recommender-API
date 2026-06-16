# database.py
import os
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "algo_recommendation_db")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000,tlsCAFile=certifi.where())
db = client[DB_NAME]

problems_collection = db["cf_problems"]
leetcode_collection = db["leetcode_problems"]

try:
    client.admin.command('ping')
    print("[database] Successfully authenticated and connected to MongoDB Atlas Cloud!")
except Exception as e:
    print(f"[database CRITICAL] Could not connect to Atlas. Check your password/IP settings. Error: {e}")

def init_db():
    try:
        problems_collection.create_index("cf_rating")
        print("[database] Index created")
    except Exception as e:
        print(f"[database] Index creation failed: {e}")
