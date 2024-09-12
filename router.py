# from enum import Enum
from fastapi import APIRouter,HTTPException,status, Depends, Request
# from deta import Deta  # Import Deta
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from typing import List

# # Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from authentication import *
from sqlalchemy.orm import Session


import backup
import schemas
import fileHandling
import implementation as imp

from database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==== GET router ====

@router.get("/")
def main():
    return RedirectResponse("/docs/")

# ==================
# PROFILE 
# ==================

@router.post("/login")  #must be the same endpoint as in OAuth2PasswordBearer
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
        ):
    return auth_login_user(form_data, db)

# temporary API point to restore backups
# ZERO SECURITY USE WITH CAUTION
# NO CHECK FOR DUPLICATES! USE WITH CAUTION!
# @router.get("/backup")
# async def load_backup(
#         db: Session = Depends(get_db)
#         ):
#     return backup.load_all(db)
    

# @router.get("/profiles",
#         # response_model = List[schemas.Profile], 
#         summary = 'Returns list of Profile objects')
# async def get_all_profiles(token: str = Depends(get_current_active_user)):
#     return next(db_profile.fetch({}))

# @router.put("/profiles/",
#         summary = 'Edits own Profile')
# async def edit_profile(input: schemas.ProfileCreate, current_user: dict = Depends(get_current_user), token: str = Depends(get_current_active_user)):
    
#     hashed_password = get_password_hash(input.password)
#     db_profile.update({'hashed_password': hashed_password}, current_user['key'])

#     return True

# @router.post("/profile")
# def add_profile(profile_req: schemas.ProfileCreate):
#     """ Create a profile to DB"""
#     # create a new profile with insert that checks if it already exists
#     # hash password   
#     hashed_password = get_password_hash(profile_req.password)

#     # insert in database if does not exist yet
#     try:
#         res1 = db_profile.insert({
#             "email":profile_req.email,
#             "hashed_password": hashed_password
#         }) 
#     except:
#         raise HTTPException(
#             status_code=409,
#             detail="User already exists"
#         )
#     return  "New User registered"

@router.get("/profile/me",
        response_model = schemas.myprofile, 
        summary = 'Returns own Profile')
async def read_my_profile(
        current_user: dict = Depends(get_current_user), 
        ):
    myprofile = {
        "email":current_user['email'],
        "key": current_user['key']
    }
    return myprofile

# ==================
# MARKETS
# ==================

@router.get("/markets/", 
        response_model = List[schemas.Market], 
        summary = 'Returns list of market objects')
async def get_all_markets(db: Session = Depends(get_db)):
    return imp.get_all_markt(db)

@router.post("/markets/",
    response_model = schemas.Market)
# async def add_market(market_req: schemas.Market, token: str = Depends(get_current_active_user)):
async def add_market(
    market_req: schemas.Market_lim, 
    token: str = Depends(get_current_active_user),
    db: Session = Depends(get_db)
    ):
    return imp.create_markt(db, market_req)
    

@router.put("/markets/{key}")
async def edit_market(
    key:str, 
    market_req: schemas.Market_lim, 
    token: str = Depends(get_current_active_user),
    db: Session = Depends(get_db)
    ):
    return imp.edit_markt(db, key, market_req)

@router.delete("/markets/{key}")
async def delete_market(
    key:str, 
    token: str = Depends(get_current_active_user),
    db: Session = Depends(get_db)
    ):
    return imp.delete_markt(db, key)
# ==================


# TEXT BLOCKS
# ==================
@router.get("/textblock/",
    response_model = List[schemas.Textblock], 
    summary = 'Returns list of textblock objects')
async def get_all_textblocks(db: Session = Depends(get_db)):
    return imp.get_all_text(db)

@router.get("/textblock/{slug}",
    response_model = schemas.Textblock, 
    summary = 'Returns one textblock object')
async def get_textblock(
    slug: str,
    db: Session = Depends(get_db)
    ):
    return imp.get_text(db, slug)

@router.put("/textblock/{slug}",
     response_model = schemas.Textblock, 
     summary = 'Edit textblock')    
async def edit_textblock(
    slug: str, 
    text_req: schemas.Textblock_lim, 
    token: str = Depends(get_current_active_user),
    db: Session = Depends(get_db)
    ):
    return imp.edit_text(db, slug, text_req)
    
@router.delete("/textblock/{slug}")
async def delete_textblock(
    slug:str, 
    token: str = Depends(get_current_active_user),
    db: Session = Depends(get_db)
    ):
    return imp.delete_text(db, slug)

## IMAGES
@router.post("/pics/",
    response_model = schemas.Image,
    summary = 'upload a picture')
async def add_image(
    imgData: schemas.ImageNew, 
    token: str = Depends(get_current_active_user),
    db: Session = Depends(get_db)
    ):
    # try:
    #fileNameOnServer, thumbNameOnServer = fileHandling.saveFileToServer(imgData.imageData, imgData.name)
    return imp.new_image(db, imgData)
    
@router.get("/pics/", 
        response_model = List[schemas.Image], 
        summary = 'Returns list of all pictures')
async def get_all_pics(db: Session = Depends(get_db)):
    return imp.get_all_images(db)
    
@router.delete("/pics/{picID}",
        summary = 'deletes a picture by key')
async def delete_picture(
    picID: str,  
    token: str = Depends(get_current_active_user),
    db: Session = Depends(get_db)
    ):
    return imp.delete_image(db, picID)

@router.put("/pics/{picID}",
        response_model = schemas.Image,
        summary = 'edits an image by ID')
async def edit_picture(
    picID: str, 
    imgData: schemas.ImageNew, 
    token: str = Depends(get_current_active_user),
    db: Session = Depends(get_db)
    ):
    return imp.edit_image(db, picID, imgData)

@router.get("pics/{slug}",
        response_model = List[schemas.Image],
        summary = "returns all images with slug")
async def get_images_by_slug(
    slug: str,
    db: Session = Depends(get_db)
    ):
    return imp.get_image(db, slug)


# @router.post("/textblock/{slug}")
# async def create_textblock(t"ext_req: schemas.Textblock, token: str = Depends(get_current_active_user)):
#     # content = next(db_textblock.fetch({"slug":slug}))
#     # if content:
#     #         raise HTTPException(
#     #         status_code=409,
#     #         detail= "Text with slug already exists, please chose editing option.")

#     # create new textblock
#     item = {
#     "title":    text_req.title,
#     "content":  text_req.content,
#     "quote":   text_req.quote,
#     "slug":     text_req.slug
#     }
#     unique_id = text_req.slug
#     db_textblock.insert(item, unique_id)
#     return item
