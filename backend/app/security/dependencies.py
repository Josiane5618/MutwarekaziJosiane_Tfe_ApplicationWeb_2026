from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer


from app.security.jwt import SECRET_KEY, ALGORITHM

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.utilisateur import Utilisateur


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        if role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès réservé à l’administrateur"
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )

