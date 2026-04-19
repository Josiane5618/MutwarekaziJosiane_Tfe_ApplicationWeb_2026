
from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    prenom: str
    nom: str
    email: EmailStr
    password: str
