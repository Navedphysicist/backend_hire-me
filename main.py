from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from db.database import Base, engine
from routers import auth, company, job, job_application, saved_job, contact
from seed.seed_data import seed_all_data

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize data
seed_all_data()

app = FastAPI(
    title="Hire Me API",
    description="API for Health Connect application",
    version="1.0.0"
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

@app.get("/")
def root():
    return {
        "message": "Welcome to Hire Me API",
        "docs": "/docs",  # Swagger UI endpoint
        "redoc": "/redoc"  # ReDoc endpoint
    }
