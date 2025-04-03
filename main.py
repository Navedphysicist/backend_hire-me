from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from db.database import Base, engine
from routers import auth, company, job, job_application, saved_job, contact
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from contextlib import asynccontextmanager
# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize data
# seed_all_data()


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield

app = FastAPI(
    title="Hire Me API",
    description="API for Hire Me application",
    version="1.0.0",
    lifespan=lifespan
)

#CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(job.router, tags=["Jobs"])
app.include_router(company.router, tags=["Companies"])
app.include_router(job_application.router, tags=["Job Applications"])
app.include_router(saved_job.router, prefix="/saved-jobs", tags=["Saved Jobs"])
app.include_router(contact.router, tags=["Contact"])

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

@app.get("/")
def root():
    return {
        "message": "Welcome to Hire Me API",
        "docs": "/docs",  # Swagger UI endpoint
        "redoc": "/redoc"  # ReDoc endpoint
    }
