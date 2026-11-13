import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from supabase import create_client, Client

'''
# Task 4: Auth - Login & Protect)
## Task 4 - STAGE 0: Setup Supabase & server
'''

# 1. Load environment variables
load_dotenv() # reads key-value pairs from .env into os.environ.

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL or SUPABASE_KEY is missing. Configure it in .env")

# 2. Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 3. Lifespan managing server startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Server running and connected to Supabase")
    yield
    print("Shutting down server...")

# 4. Core FastAPI App
app = FastAPI(
    title="Task 4: Auth API (Supabase + FastAPI)",
    version="1.4.0-alpha.1",
    description="Authentication API with Supabase: signup, login, logout, and protected routes.",
    lifespan=lifespan
)

# Discovery & Health Endpoints
@app.get("/")
async def root():
    return {
        "message": "Server running & connected to Supabase"
    }
