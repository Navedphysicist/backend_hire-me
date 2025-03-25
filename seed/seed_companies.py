from db.database import SessionLocal
from models.company import DbCompany
import json

def seed_companies():
    db = SessionLocal()
    try:
        # Load the companies data from JSON
        with open('seed/companies.json', 'r') as f:
            companies_data = json.load(f)

        # Update each company with additional fields
        for company_data in companies_data:
            company_name = company_data['company_name']
            
            # Find existing company
            existing_company = db.query(DbCompany).filter(
                DbCompany.company_name == company_name
            ).first()

            if existing_company:
                # Update existing company with new fields
                existing_company.company_description = company_data['company_description']
                existing_company.remote = company_data['remote']
                existing_company.company_location = company_data['company_location']
                existing_company.company_type = company_data['company_type']
                existing_company.industry_type = company_data['industry_type']
                existing_company.business_nature = company_data['business_nature']
                existing_company.employee_count = company_data['employee_count']
            else:
                print(f"Company {company_name} not found in database")

        # Commit all changes
        db.commit()
        print("Successfully updated companies with additional information!")

    except Exception as e:
        db.rollback()
        print(f"Error updating companies: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_companies()
