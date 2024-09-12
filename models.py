from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, LargeBinary
# from sqlalchemy.orm import relationship

from database import Base

class Markt(Base):
    __tablename__ = "markt"
    id = Column(Integer, primary_key = True)
    name = Column(String(200))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    link = Column(String(2083))

class Text(Base):
    __tablename__ = "textblock"
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    quote = Column(String(800))
    content = Column(String(2083))
    slug = Column(String(200))

class Image(Base):
    __tablename__ = "image"
    id = Column(Integer, primary_key=True)
    description = Column(String(200))
    slug = Column(String(20), default="gallery")
    order = Column(Integer)
    thumb = Column(String(200))
    thumbUrl= Column(String(200))
    file = Column(String(200))
    url = Column(String(200))

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(200))
    email = Column(String(200))
    passwordHash = Column(String(200))