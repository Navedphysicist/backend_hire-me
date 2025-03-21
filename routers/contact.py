from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

router = APIRouter()


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str


@router.post("/contact")
def submit_contact_form(contact: ContactForm):
    # Here you would typically send an email or store the contact form data
    # For now, we'll just return a success message
    return {"message": "Contact form submitted successfully"}
