

from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    prenom: str
    nom: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
