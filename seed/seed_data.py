from db.database import SessionLocal
from models.company import DbCompany
from models.job import DbJob
import json

def seed_all_data(user_ids: list[int] = [1, 2, 3]):
    """
    Single function to handle both jobs and companies seeding
    using a single database session
    """
    db = SessionLocal()
    try:
        # Load both data files
        with open('seed/companies.json', 'r') as f:
            companies_data = json.load(f)
        
        with open('seed/jobs.json', 'r') as f:
            jobs_data = json.load(f)

        # First check if data already exists
        existing_companies = db.query(DbCompany).count()
        if existing_companies > 0:
            print("Data already exists. Checking for updates...")
            # Update existing companies and create new ones if needed
            current_user_idx = 0
            
            for company_data in companies_data:
                company_name = company_data['company_name']
                existing_company = db.query(DbCompany).filter(
                    DbCompany.company_name == company_name
                ).first()
                
                if existing_company:
                    # Update existing company
                    existing_company.company_description = company_data['company_description']
                    existing_company.remote = company_data['remote']
                    existing_company.company_location = company_data['company_location']
                    existing_company.company_type = company_data['company_type']
                    existing_company.industry_type = company_data['industry_type']
                    existing_company.business_nature = company_data['business_nature']
                    existing_company.employee_count = company_data['employee_count']
                    print(f"Updated existing company: {company_name}")
                else:
                    # Create new company
                    new_company = DbCompany(
                        company_name=company_name,
                        company_avatar=company_data['company_avatar'],
                        company_description=company_data['company_description'],
                        remote=company_data['remote'],
                        company_location=company_data['company_location'],
                        company_type=company_data['company_type'],
                        industry_type=company_data['industry_type'],
                        business_nature=company_data['business_nature'],
                        employee_count=company_data['employee_count'],
                        owner_id=user_ids[current_user_idx]
                    )
                    db.add(new_company)
                    current_user_idx = (current_user_idx + 1) % len(user_ids)
                    print(f"Created new company: {company_name}")
            
            db.commit()
            print("Successfully updated and created companies!")
            return
        
        # If no data exists, create everything from scratch
        print("No existing data found. Creating new data...")
        
        # Keep track of created companies
        created_companies = {}
        current_user_idx = 0

        # First create all companies from companies.json
        for company_data in companies_data:
            company_name = company_data['company_name']
            company = DbCompany(
                company_name=company_name,
                company_avatar=company_data['company_avatar'],
                company_description=company_data['company_description'],
                remote=company_data['remote'],
                company_location=company_data['company_location'],
                company_type=company_data['company_type'],
                industry_type=company_data['industry_type'],
                business_nature=company_data['business_nature'],
                employee_count=company_data['employee_count'],
                owner_id=user_ids[current_user_idx]
            )
            db.add(company)
            db.flush()  # Get the company ID
            created_companies[company_name] = company
            current_user_idx = (current_user_idx + 1) % len(user_ids)
            print(f"Created company: {company_name}")

        # Now create all jobs
        for job_data in jobs_data:
            company_name = job_data['company_name']
            company = created_companies.get(company_name)
            
            if company:
                job = DbJob(
                    company_name=company_name,
                    company_avatar=job_data['company_avatar'],
                    job_title=job_data['job_title'],
                    job_description=job_data['job_description'],
                    salary=float(job_data['salary']),
                    place=job_data['place'],
                    skills=job_data['skills'],
                    job_type=job_data['job_type'],
                    work_mode=job_data['work_mode'],
                    experience_level=job_data['experience_level'],
                    company_id=company.id,
                    creator_id=company.owner_id
                )
                db.add(job)
                print(f"Created job: {job_data['job_title']} for {company_name}")

        # Commit all changes
        db.commit()
        print("Successfully created all new data!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_all_data()
