from sqlalchemy.orm import Session
from fastapi import HTTPException, status

import models 
import fileHandling
import schemas 
import crud_sql as crud


def create_markt(db: Session, newMarkt:schemas.Market_lim):
    '''
        creates one new markt based on schemas.Market_lim 
    '''
    item = {
    "market_name":  newMarkt.market_name,
    "start_date":   newMarkt.start_date,
    "end_date":     newMarkt.end_date,
    "infotext":     newMarkt.infotext,
    "link":         newMarkt.link,
     }
    
    try:
        return crud.new(db, "markt", item)
    except:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=    "Markt {} konnte nicht erstellt werden".format(newMarkt.market_name)
            )

def get_all_markt(db: Session):
    ''' 
        returns a list of all markt objects
    '''
    try:
        return crud.get_all(db, "markt")
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=    "Maerkte konnten nicht aus der Datenbank gelesen werden."
            )

def get_markt(db: Session, id:int):
    '''
        returns single markt by ID
    '''
    try:
        return crud.get_one(db, "markt", id)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=    "Markt mit ID {} nicht gefunden.".format(id)
            )    

def delete_markt(db: Session, id: int):
    '''
        deletes markt based on id 
    '''
    try:
        return crud.delete_one(db, "markt", id)
    except:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=    "Markt mit ID {} konnte nicht geloescht werden.".format(id)
            )
    
def edit_markt(db: Session, id: int, editedMarkt: schemas.Market):
    '''
        overwrites name, start_date, end_date and link with the values from editedMarkt
    '''
    try:
        return crud.edit_one(db, "markt", id, editedMarkt)
    except:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=    "Markt mit ID {} konnte nicht bearbeitet werden.".format(id)
            )

#### IMAGES AND GALLERY
def get_all_markt(db: Session):
    ''' 
        returns a list of all picture objects
    '''
    try:
        return crud.get_all(db, "pics")
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=    "Bilder konnten nicht aus der Datenbank gelesen werden."
            )

def get_markt(db: Session, id:int):
    '''
        returns single picture by ID
    '''
    try:
        return crud.get_one(db, "pics", id)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=    "Bild mit ID {} nicht gefunden.".format(id)
            )    

def delete_image(db: Session, id: int):
    '''
        delete an image based on id
    '''
    picData = crud.get_one.get(db, "pics", id)
    pic = schemas.Image(**picData)
    print(pic)
    if pic:
        try:
            pic_is_deleted = fileHandling.deleteFileFromServer(pic.file)
            thumb_is_deleted = fileHandling.deleteFileFromServer(pic.thumb)
            crud.delete_one(db, "pics", id)
            return pic_is_deleted
        except:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Could not delete image {}.".format(pic.file)
                )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=    "No image with ID {}.".format(id)
            )
    
def new_image(db: Session, newImage: schemas.ImageNew):
    imgPath, imgUrl = fileHandling.saveImgToServer(newImage.imageData, newImage.name)
    thumbPath, thumbUrl = fileHandling.saveThumbToServer(newImage.imageData, newImage.name)
    # except:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Failed to save image {}".format(imgData.name)
    #         )
    try:
        item = {
        "order":        newImage.order,
        "slug":         newImage.slug,
        "file":         imgPath,
        "thumb":        thumbPath,
        "url":          imgUrl,
        "thumbUrl":     thumbUrl,
        "description":  newImage.description,
        }
    except:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not assemble image data {}".format(newImage.name)
            )
    try:
        dbObject = crud.new(db,"pics",item)
        return dbObject
    except: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database did not accept new {}.".format(newImage.name)
            )

def edit_image(db: Session, id: int, imgData: schemas.ImageNew):
    # fetch old data
    oldPicData = crud.get_one(db, "pics", id)
    oldPic = schemas.Image(**oldPicData)
    if not oldPic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No image with ID {}.".format(id)
            )
    else:
        new_img_data = crud.edit_one(db, "pics", id,
                {
                'description': imgData.description, 
                'slug': imgData.slug,
                'order': imgData.order
                }
            )

        # check if we have to re-upload the picture:
        if imgData.name:
            try:
                # upload new file
                imgPath, imgUrl = fileHandling.saveImgToServer(imgData.imageData, imgData.name)
                thumbPath, thumbUrl = fileHandling.saveThumbToServer(imgData.imageData, imgData.name)
                # delete old file
                deleted = fileHandling.deleteFileFromServer(oldPic.file)
                deletedThumb = fileHandling.deleteFileFromServer(oldPic.thumb)

                # set DB values
                new_img_data =crud.edit_one(db, "pics", id, 
                        {
                        'file': imgPath,
                        'url': imgUrl,
                        'thumb': thumbPath,
                        'thumbUrl': thumbUrl
                        }
                    )
            except:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to save image {}".format(imgData.name)
                    )

        # return the edited image:
        return new_img_data


#### textblocks
def get_all_text(db):
    '''
        returns all texblocks as list
    '''
    try:
        return crud.get_all(db, "text")
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=    "Textbloecke konnten nicht aus der Datenbank gelesen werden."
            )

def get_text(db, slug):
    try:
        return crud.get_one_by_slug(db, "text", slug)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=    "Textblock '{}' nicht gefunden.".format(slug)
            ) 

def edit_text(db, slug, data):

    # fetch object to match ID with slug
    try:
        text_item = crud.get_one_by_slug(db, "text", slug)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=    "Textblock '{}' nicht gefunden.".format(slug)
            ) 
    # get ID since we originally only have slug
    id = text_item['id']
    try:
        return crud.edit_one(db, "text", id, data)
    except:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=    "Textblock '{}' konnte nicht bearbeitet werden.".format(slug)
            )

def delete_text(db, slug):
    # fetch object to match ID with slug
    try:
        text_item = crud.get_one_by_slug(db, "text", slug)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=    "Textblock '{}' nicht gefunden.".format(slug)
            ) 
    # get ID since we originally only have slug
    id = text_item['id']
    
    try:
        return crud.delete_one(db, "text", id)
    except:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=    "Textblock mit ID {} konnte nicht geloescht werden.".format(id)
            )


# def edit_image(db: Session, id: int, editedImage: schemas.Image ):
#     '''
#         actually not needed, right?
#         maybe onlye to edit the description... 
#     '''
#     obj = db.query(models.Image).filter(models.Image.id == id).first()
#     obj.imageData = editedImage.imageData
#     obj.description = editedImage.description
#     obj.useCase = editedimage.useCase
#     return db.query(models.Image).filter(models.Image.id == id).first()