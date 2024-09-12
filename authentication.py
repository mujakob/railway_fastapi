# Security
from fastapi import APIRouter,HTTPException,status, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt import PyJWTError 
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Union, Dict
from sqlalchemy.orm import Session


import crud_sql as crud

from database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==== DATA BASE ====
# Initialize with a Project Key

# JWT
# replace the secret key with the output of `openssl rand -hex 32`
SECRET_KEY = "tatrdeMPPMUaaAnkH1bOXP41BY6V+F87Y2p1JWZTZV4="
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
# =======

user_count=0

# Security: OAuth and passlib functions
# ===========================#
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
pwd_context   = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    res = pwd_context.verify(plain_password, hashed_password)
    return res

def get_password_hash(password):
    hashed_pass = pwd_context.hash(password)
    return hashed_pass

def authenticate_user(db: Session, email: str, password: str):
    user = crud.get_user(db, email)

    if not user:
        return False
    user = dict(user[0])
    if not verify_password(password, user['hashed_password']):
        print("Debug password cannot be verified")
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(db=Depends(get_db), token: str = Depends(oauth2_scheme)):
# async def get_current_user():
    """token is access_token in login function"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        email: str = payload.get("sub")

        if email is None:
            raise credentials_exception
    
    except PyJWTError:
        raise credentials_exception
    
    
    # email = 'string'
    user = crud.get_user(db, email)
        
    if not user:
        raise HTTPException(
            status_code=409,
            detail="im not a user" + str(user),
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = dict(user[0])
    return user

async def get_current_active_user(current_user: dict =  Depends(get_current_user)):
    return current_user

async def auth_login_user(form_data):
    # OAuth form data has username, but the frontend passes the email
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # the sub key should have a unique identifier across the entire application
    # and it should be a string.
    access_token = create_access_token(data={"sub": user["email"]},
                                       expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}
