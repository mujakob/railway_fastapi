from sqlalchemy.orm import Session

import models
import schemas

TABLES = {
    # dict to select the right table based on type
    "pics": models.Image,
    "text": models.Text,
    "markt": models.Markt,
    "user": models.User
}

def get_user(db: Session, email: str):
    return db.query(models.User).filter(models.User.email==email).first()

def put_user(db: Session, data):
    db_item = models.User(data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item 

def get_one(db: Session, type: str, id):
    return db.query(TABLES[type]).filter(TABLES[type].id == id).first()

def get_one_by_slug(db: Session, type: str, slug):
    return db.query(TABLES[type]).filter(TABLES[type].slug == slug).first()

def get_all(db: Session, type: str, skip=0, limit=1000):
    return db.query(TABLES[type]).offset(skip).limit(limit).all()


def edit_one(db: Session, type: str, id, data):
    """
    based on https://stackoverflow.com/questions/63143731/update-sqlalchemy-orm-existing-model-from-posted-pydantic-model-in-fastapi
    Using a new update method seen in FastAPI https://github.com/tiangolo/fastapi/pull/2665
    Simple, does not need each attribute to be updated individually
    Uses python in built functionality... preferred to the pydintic related method
    """

    # get the existing data
    db_item = db.query(TABLES[type]).filter(TABLES[type].id == id).one_or_none()
    if db_item is None:
        return None

    # Update model class variable from requested fields 
    for var, value in vars(data).items():
        setattr(db_item, var, value) if value else None

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def new(db: Session, type: str, data):
    db_item = TABLES[type](**data.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_one(db: Session, type: str, id):
    db_item = db.query(TABLES[type]).filter(TABLES[type].id == id).one_or_none()
    if db_item is None:
        return None    
    db_item.delete(synchronize_session=False)
    db.commit()
    return True

