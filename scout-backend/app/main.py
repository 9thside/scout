from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Scout API", description="Personal Shopping Agent API")

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Import and include routers
from app.routes.auth import router as auth_router
from app.routes.searches import router as searches_router
from app.routes.alerts import router as alerts_router

app.include_router(auth_router)
app.include_router(searches_router)
app.include_router(alerts_router)

# Initialize database on startup
from app.database import init_db


@app.on_event("startup")
def startup():
    init_db()


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
