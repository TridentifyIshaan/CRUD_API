import os # for operating system interactions (accessing environment variables)
from contextlib import asynccontextmanager # for managing server startup/shutdown
from dotenv import load_dotenv # for reading environment variables from .env
from fastapi import FastAPI, HTTPException, Request, Header # for raising HTTP errors
from fastapi.exceptions import RequestValidationError # for request body validation errors
from fastapi.responses import JSONResponse # for returning JSON responses
from pydantic import BaseModel # for defining request/response bodies
from supabase import create_client, Client # for connecting to Supabase

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
    version="1.4.0-alpha.4",
    description="Authentication API with Supabase: signup, login, logout, and protected routes.",
    lifespan=lifespan
)

# ---- Discovery & Health Endpoints ---- 
@app.get("/")
async def root():
    return {
        "message": "Server running & connected to Supabase"
    }

# ---- Standard Error Format Handlers ----
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else exc.detail.get("error", str(exc.detail))
    return JSONResponse(status_code=exc.status_code, content={"error": detail})
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Email and password are required"})

# Task 4 - STAGE 1: Open auth: Sign Up & Log In
# 1. Define the incoming JSON body shape
class AuthRequest(BaseModel):
    email: str
    password: str

# 2. Define the FastAPI POST endpoint for signup
@app.post("/auth/signup", status_code=201)
async def signup(credentials:AuthRequest):
    # Validate non-empty/non-blank fields
    email = credentials.email.strip()
    password = credentials.password.strip()
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    # Supabase call (referred from official docs)
    try:
        response = supabase.auth.sign_up(
            {
                "email": email,
                "password": password,
            }
        )
        return response.user
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# 3. Define the FastAPI POST endpoint for Login
@app.post("/auth/login")
async def login(credentials:AuthRequest):
    # Validate non-empty/non-blank fields
    email = credentials.email.strip()
    password = credentials.password.strip()
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    # Supabase call (referred from official docs)
    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )
        if not response.session:
            raise HTTPException(status_code=401, detail="Invalid login credentials")

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": response.session.token_type,
            "user": response.user
        }
    except HTTPException:
        raise 
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login credentials")

# Task 4 - STAGE 2: The public & protected gates
# 1. Public Endpoint (No auth required)
@app.get("/public/info")
async def public_info():
    return {
        "message": "Welcome stranger! This info is public."
    }

# Task 4 - STAGE 3: The guard: token verification
@app.get("/protected/profile")
async def protected_profile(authorization: str | None = Header(None)):
    # 1. Extract and check Authorization header (from Stage 2)
    if not authorization:
        raise HTTPException(status_code=401, detail="Access token required")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise HTTPException(status_code=401, detail="Access token required")

    token = parts[1].strip()

    # 2. Ask Supabase whether the token is authentic and valid
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        user = user_response.user

        # 3. Return safe metadata
        return {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at
        }
    except HTTPException:
        raise
    except Exception:
        # Token was tampered with, expired, or malformed
        raise HTTPException(status_code=401, detail="Invalid or expired token")