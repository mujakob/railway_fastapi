from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import enum
from datetime import date 
from pydantic.json import timedelta_isoformat


class Login(BaseModel):
    password: str
    email: str

class ProfileBase(BaseModel):
    email: str

    class Config:
        orm_mode = True

class ProfileCreate(ProfileBase):
    password: str

class Profile(ProfileCreate):
    id: str

class myprofile(BaseModel):
    email: str
    id: str

class Market_lim(BaseModel):
    market_name: str
    start_date: Optional[str] = ''
    end_date: Optional[str] = ''
    infotext: Optional[str] = ''
    link: Optional[str] = ''
    class Config:
        orm_mode = True
class Market(Market_lim):
    id: str

class Textblock_lim(BaseModel):
    title : Optional[str]
    content  : str
    quote : Optional[str]

class Textblock(Textblock_lim):
    slug : str

class ImageNew(BaseModel):
    imageData: Optional[str]
    description: Optional[str]
    slug: Optional[str]
    order: Optional[int]
    name: Optional[str]

class Image(BaseModel): 
    id: str   
    description: Optional[str]
    slug: str
    order: Optional[int]
    file: str
    thumb: Optional[str]
    url: str
    thumbUrl: Optional[str]
    class Config:
        orm_mode = True

class ImageForDB(BaseModel):
    description: Optional[str]
    slug: str
    order: Optional[int]
    file: str
    thumb: Optional[str]
    url: str
    thumbUrl: Optional[str]

# Security
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str = None


