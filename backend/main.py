# FastAPI Entry Point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import posts, campaigns, publish
from db.connection import startup_db, shutdown_db
import os

app = FastAPI(title="Digital Media AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated/watermarked images
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(os.path.join(STATIC_DIR, "generated"), exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(posts.router,     prefix="/api/posts",     tags=["posts"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(publish.router,   prefix="/api/publish",   tags=["publish"])

@app.on_event("startup")
async def startup():
    await startup_db()

@app.on_event("shutdown")
async def shutdown():
    await shutdown_db()

@app.get("/")
async def root():
    return {"status": "Digital Media AI running"}