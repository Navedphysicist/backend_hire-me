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
    return {"message": "Contact form submitted successfully"}
