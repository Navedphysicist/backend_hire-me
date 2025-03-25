from db.database import SessionLocal
from models.company import DbCompany
from models.job import DbJob
import json

def seed_companies_and_jobs(user_ids: list[int] = [1, 2, 3]):
    db = SessionLocal()
    try:
        # Check if companies already exist
        existing_companies = db.query(DbCompany).count()
        if existing_companies > 0:
            print("Companies and jobs data already exists. Skipping seeding.")
            return

        # Load the job data from the JSON
        with open('seed/jobs.json', 'r') as f:
            jobs_data = json.load(f)

        # Keep track of created companies to avoid duplicates
        created_companies = {}
        current_user_idx = 0

        for job_data in jobs_data:
            company_name = job_data['company_name']
            
            # Create company if it doesn't exist
            if company_name not in created_companies:
                company = DbCompany(
                    company_name=company_name,
                    company_avatar=job_data['company_avatar'],
                    owner_id=user_ids[current_user_idx]  # Round-robin assignment of companies to users
                )
                db.add(company)
                db.flush()  # Flush to get the company ID
                created_companies[company_name] = company
                
                # Move to next user ID in round-robin fashion
                current_user_idx = (current_user_idx + 1) % len(user_ids)

            company = created_companies[company_name]
            
            # Create job
            job = DbJob(
                company_name=company_name,  # Add company name to job as well
                company_avatar=job_data['company_avatar'],  # Add company avatar to job as well
                job_title=job_data['job_title'],
                job_description=job_data['job_description'],
                salary=float(job_data['salary']),
                place=job_data['place'],
                skills=job_data['skills'],
                job_type=job_data['job_type'],
                work_mode=job_data['work_mode'],
                experience_level=job_data['experience_level'],
                company_id=company.id,
                creator_id=company.owner_id  # Job creator is same as company owner
            )
            db.add(job)

        # Commit all changes
        db.commit()
        print("Successfully seeded companies and jobs data!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding companies and jobs: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_companies_and_jobs()
