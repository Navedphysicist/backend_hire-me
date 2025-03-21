# Hire Me - Job Networking Platform

A simplified job networking platform similar to LinkedIn, built using FastAPI, SQLAlchemy ORM, and SQLite.

## Features

- User registration and authentication
- Company management
- Job posting and management
- Job applications
- Job saving functionality
- View posted jobs and applications

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd backend_hire-me
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- POST `/register` - Register a new user
- POST `/token` - Login and get access token

### Companies
- POST `/companies/` - Create a new company
- GET `/companies/` - List all companies for the current user
- GET `/companies/{company_id}` - Get details of a specific company

### Jobs
- POST `/jobs/` - Create a new job posting
- GET `/jobs/` - List all jobs created by the current user
- GET `/jobs/{job_id}` - Get details of a specific job

### Job Applications
- POST `/applications/` - Apply for a job
- GET `/applications/` - List all job applications by the current user

### Saved Jobs
- POST `/saved-jobs/` - Save a job for later
- GET `/saved-jobs/` - List all saved jobs
- DELETE `/saved-jobs/{saved_job_id}` - Remove a saved job

## Database

The application uses SQLite as the database. The database file (`hire_me.db`) will be created automatically when you first run the application.

## Security

- Passwords are hashed using bcrypt
- JWT tokens are used for authentication
- All endpoints (except registration and login) require authentication

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
