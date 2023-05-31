
from datetime import datetime, timedelta
import jwt
from fastapi.security import HTTPBearer
from fastapi import Depends, HTTPException
from pydantic import ValidationError

SECURITY_ALGORITHM = 'HS256'
SECRET_KEY = 'ebook'

def generate_token(id:str) -> str:
    expire = datetime.utcnow() + timedelta(
        seconds=60 * 60 * 24 * 30  # Expired after 30 days
    )
    to_encode = {
        "exp": expire, "_id": id, 
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=SECURITY_ALGORITHM)
    return encoded_jwt

reusable_oauth2 = HTTPBearer(
    scheme_name='Authorization'
)


def validate_token(http_authorization_credentials=Depends(reusable_oauth2)) -> str:
    try:
        payload = jwt.decode(http_authorization_credentials.credentials, SECRET_KEY, algorithms=[SECURITY_ALGORITHM])
        if payload.get('exp') < datetime.now().timestamp():
            raise HTTPException(status_code=401, detail="Token expired")
        return payload.get('_id')
    except:
        raise HTTPException(
            status_code=401,
            detail=f"Could not validate credentials",
        )
