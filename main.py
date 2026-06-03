import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import ALFA_API_BASE

app = FastAPI(
    title="NextPrep Problem Recommender API",
    description="Smart LeetCode recommendations driven by your mastery vector, not random grinding",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_methods=["*"],
    allow_headers=["*"],
)
