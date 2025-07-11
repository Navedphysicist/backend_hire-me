from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from db.database import Base, engine
from routers import auth, company, job, job_application, saved_job, contact
from core.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hire Me API",
    description="API for Hire Me application"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Mount static files directory only locally
if not settings.VERCEL:
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(job.router, tags=["Jobs"])
app.include_router(company.router, tags=["Companies"])
app.include_router(job_application.router, tags=["Job Applications"])
app.include_router(saved_job.router, tags=["Saved Jobs"])
app.include_router(contact.router, tags=["Contact"])


@app.get("/")
def root():
    return {
        "message": "Welcome to Hire Me API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

    # 16
    # 12
    # 7
    # 6
    # 5
    # 806 = 12