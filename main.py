from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from LEETCODE.routes.recommend import router as leetcode_router
from cf.router import router as cf_router

app = FastAPI(
    title="Nexprep - LeetCode & Codeforces Recommender",
    description="Smart recommendations for LeetCode and Codeforces driven by your mastery vector",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
)

app.include_router(leetcode_router, prefix="/api/v1")
app.include_router(cf_router) 