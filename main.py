from fastapi import FastAPI
from db.database import Base, engine
from routers import auth, company, job, job_application, saved_job, contact
from seed.seed_jobs import seed_companies_and_jobs
from seed.seed_companies import seed_companies

# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Hire Me API",
    description="API for Health Connect application",
    version="1.0.0"
)

# Include routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(job.router, tags=["Jobs"])
app.include_router(company.router, tags=["Companies"])
app.include_router(job_application.router, tags=["Job Applications"])
app.include_router(saved_job.router, prefix="/saved-jobs", tags=["Saved Jobs"])
app.include_router(contact.router, tags=["Contact"])


seed_companies_and_jobs()
seed_companies()

@app.get("/")
def root():
    return {
        "message": "Welcome to Hire Me API",
        "docs": "/docs",  # Swagger UI endpoint
        "redoc": "/redoc"  # ReDoc endpoint
    }
