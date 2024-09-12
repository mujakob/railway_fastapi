# import pysftp
import ftplib
import base64
import tempfile
import posixpath
import os
from collections import namedtuple
from fastapi import HTTPException, status
from PIL import Image


class ftpData:
    serverType = 'ftp'
    host = "sv65.domainunion.de"
    user = "mujakob"
    password = "WTF1ddl03?"
    port = '21'

FTPDATA = ftpData()

IMGDIR = '/files.grimm-mueller.de/imageHost/upload'
THUMBDIR = '/files.grimm-mueller.de/imageHost/upload/thumbs'

IMGURL = 'https://files.grimm-mueller.de/imageHost/upload'
THUMBURL = 'https://files.grimm-mueller.de/imageHost/upload/thumbs'

THUMBHEIGHT = 200
THUMBWIDTH = 200



# def loadTestFile(file="src/testImg.txt"):
#     f = open(file, "r")
#     fileString = f.read()
#     f.close()
#     return fileString

# def loadTestImg(file="src/testPNG.png"):
#     with open(file, 'rb') as f:
#         content = f.read()
#         encoded = base64.b64encode(content)
#         f.close()

#     return encoded

def cdTree(currentDir, ftp):
    '''
    recursively recreates the missing directories, curtesy of lecnt
    https://stackoverflow.com/questions/10644608/create-missing-directories-in-ftplib-storbinary
    '''
    if currentDir != "":
        try:
            ftp.cwd(currentDir)
        except:
            cdTree("/".join(currentDir.split("/")[:-1]), ftp)
            ftp.mkd(currentDir)
            ftp.cwd(currentDir)

def create_thumbnail(infile, mHeight: int = THUMBHEIGHT, mWidth: int = THUMBWIDTH):
    '''
    creates a tempfile for the thumbnail
    '''
    # open
    thumbSize = (mWidth, mHeight)

    # store as tempfile
    tempOutFile = tempfile.TemporaryFile()
    
    # try:
    with Image.open(infile) as im:
        im.thumbnail(thumbSize)
        RGBim = im.convert('RGB') # conversion for JPG reasons!
        RGBim.save(tempOutFile, "JPEG")

        tempOutFile.seek(0)
        
        return tempOutFile

    # except OSError:
    #     print("cannot create thumbnail for", infile)
    #     return False 

def writeStringToFile(imgString: base64):
    '''
    yields a tempfile object containing the img (from base64)
    '''
    tempImg = tempfile.TemporaryFile()
    # clipping the "data" part from the string:
    b64String = imgString.split(',')[1]
    # writing bas64 string to temp file
    tempImg.write(base64.b64decode(b64String))
    # reset pointer for future read:
    tempImg.seek(0)
    print('temp file created...')
    return tempImg

def saveToServer(imgFile: tempfile, fileName: str, directory: str = IMGDIR):
    '''
    stores a tempfile object to the server set in global ftpData
    returns filename (without path) on server
    '''

    # create filepath on server
    theNameToStore = fileName
    theStoredLocation = posixpath.join(directory, theNameToStore)
    print(theStoredLocation)

    print('connecting FTP')
    with ftplib.FTP(FTPDATA.host) as session:
        session.login(user=FTPDATA.user, passwd=FTPDATA.password)

        # go to right directory:
        try:
            session.cwd(directory)
        except:
            print(f'have to create target directory {directory}')
            cdTree(directory, session)


        if session.pwd() == directory:
            print('we are in the right directory!')
        else:
            print('wrong directory - ABORT')
            print(session.pwd())
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Problems in finding server directory: {directory}"
                )

        ## check if file exists and rename
        dirContents = session.nlst(directory)
        print(dirContents)
        i = 0
        while dirContents.__contains__(theStoredLocation):
            i +=1
            ## add an integer to the filename
            (root, ext) = os.path.splitext(fileName)
            theNameToStore = root + str(i) + ext

            theStoredLocation = posixpath.join(directory, theNameToStore) 
       
        if i > 0:
            print(f'renamed the file to {theNameToStore}')    

        # send file:
        # reset pointer for read:
        imgFile.seek(0)
        # print(imgFile.read())
        session.storbinary(f'STOR {theStoredLocation}', imgFile)

        # check if file has arrived
        dirContents = session.nlst(directory)
        print(dirContents)
        if dirContents.__contains__(theStoredLocation):
            print('everything all right...')
        else: 
            print(' Could not find the uploaded file?')
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail="Failed to save image on server {}".format(theNameToStore)
                )

        session.quit()
        return theNameToStore


def saveThumbToServer(file:base64, imgName: str):
    # create temp file
    tempImg = writeStringToFile(file)
    # resize to thumb size
    resizedFile = create_thumbnail(tempImg)
    # upload to server
    fileNameOnServer = saveToServer(resizedFile, imgName, THUMBDIR)
    # create path and url to return for DB
    path = posixpath.join(THUMBDIR, fileNameOnServer)
    url = posixpath.join(THUMBURL, fileNameOnServer)
    return path, url

def saveImgToServer(file: base64, imgName: str):
    # create temp file
    tempImg = writeStringToFile(file)
    # upload to server
    fileNameOnServer = saveToServer(tempImg, imgName, IMGDIR)
    # create path and url to return for DB
    path = posixpath.join(IMGDIR, fileNameOnServer)
    url = posixpath.join(IMGURL, fileNameOnServer)
    return path, url




############ LEGACY FUNCTION
def saveFileToServer( file: base64, targetName="img", targetDir=IMGDIR, server = FTPDATA ):
    
    with tempfile.TemporaryFile() as tempFile:
        # creating dummy bas64 string
        # sourceString = loadTestImg()
        sourceString = file

        # clipping the "data" part from the string:
        b64String = sourceString.split(',')[1]
        # writing bas64 string to temp file
        tempFile.write(base64.b64decode(b64String))
        # reset pointer for future read:
        tempFile.seek(0)
        print('temp file created...')

        theStoredLocation = posixpath.join(targetDir, targetName)
        print(theStoredLocation)

        # thumbnail creation
        thumb = create_thumbnail(tempFile)
        theThumbLocation = posixpath.join(THUMBDIR, targetName)

        theNameToStore = targetName

        # if server.serverType == 'sftp':
        #     ## SFTP NEEDS SOME MORE LOVE AND REFINEMENT!
        #     print('connecting SFTP')
        #     with pysftp.Connection(host=server.host, username=server.user, password=server.password, port=server.port) as sftp:
        #         print("Connection succesfully stablished ... ")

        #         # Define the remote path where the file will be uploaded
        #         sftp.put(tempFile, theStoredLocation)
            

        # elif server.serverType == 'ftp':



        print('connecting FTP')
        with ftplib.FTP(server.host) as session:
            session.login(user=server.user, passwd=server.password)

            # go to right directory:
            try:
                session.cwd(targetDir)
            except:
                print(f'have to create target directory {targetDir}')
                cdTree(targetDir, session)


            if session.pwd() == targetDir:
                print('we are in the right directory!')
            else:
                print('wrong directory - ABORT')
                print(session.pwd())
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Problems in finding server directory"
                    )

            ## check if file exists and rename
            dirContents = session.nlst(targetDir)
            print(dirContents)
            i = 0
            while dirContents.__contains__(theStoredLocation):
                i +=1
                ## add an integer to the filename
                (root, ext) = os.path.splitext(targetName)
                theNameToStore = root + str(i) + ext

                theStoredLocation = posixpath.join(targetDir, theNameToStore) 

                theThumbLocation = posixpath.join(THUMBDIR, theNameToStore)

            
            if i > 0:
                print(f'renamed the file to {theNameToStore}')    

            # send file:
            # reset pointer for read:
            tempFile.seek(0)
            print(tempFile.read())
            session.storbinary(f'STOR {theStoredLocation}', tempFile)

            # send thumb:
            session.storbinary(f'STOR {theThumbLocation}', thumb)

            # check if file has arrived
            dirContents = session.nlst(targetDir)
            print(dirContents)
            if dirContents.__contains__(theStoredLocation):
                print('everything all right...')
            else: 
                print(' Could not find the uploaded file?')
                raise HTTPException(
                    status_code=status.HTTP_417_EXPECTATION_FAILED,
                    detail="Failed to save image on server {}".format(theNameToStore)
                    )

            session.quit()

        theStoredLocationURL = posixpath.join(IMGURL, theNameToStore)
        theThumbLocationURL = posixpath.join(THUMBURL, theNameToStore)

        return theStoredLocationURL, theThumbLocationURL

def deleteFileFromServer(targetName="", server=ftpData):
    
    with ftplib.FTP(server.host) as session:
        session.login(user=server.user, passwd=server.password)

        # go to right directory:
        try:
            response = session.delete(targetName)
            return response
        except:
            return False


# ###########################################################################

def main():
    # file = loadTestImg()
    print('meep')
    testImg = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAEmUlEQVRYR72XX0xbdRTHv7+2tIVC6Tagbej4MxkoGTBl8k9AITrMYJolDhKY2RsPxndN/BNNNPq46IvyYINhM0SYURKZwioIsqK0Nl2RFbBsFIa57Sx/2tuW9t5rboMLrLS7dLCT3Lfz53POPb/zOz/icDh8Go0mmWVZDgKFEAKGYRAKhTifz8e5XC5mYWEh5HQ6w7FciMNhkmO9KVPPz0nJ+gaRBIPEWVa2RiiK4jIzMwWGjq+2vLyM0dFRUBS1Q5GwLEquG6CkKATlctx++iTy/5hCSCYDWVpaCmVnZ0v2hWDLyeDgIOx2+32X+WYzsmduIZCWhpn6evhU6ThuNEJG06EogFAoBL/fD5FIFJOJZVmIxWIoFIqYOr29vVhZWUE6RaHY8AtACKxNTZHgvGTb7QimpPiiAKanpzE0NPRQAB4wPT0dOp0O5eXlUKlUO2BomkZXVxee+f4HJPt8cOXnY7a66r6OZHMTYal0NQrAarXCYDDs6Y/wTdna2gqtVrvDbviTT3G4rw+LpSVYLCkBG13VaID/K7AnAgAymQydnZ2RXxMRjoOloRE0w8B8toXPdjeX+wfAe29paUFBQUEkkPOjj/HvwABunG1BIDU1Vj77C1BdXY3KykqEPR78daYZ8pNl+LGoKF4x9xegqqoK/DfbcQFB5yJy9Xp8NTDw+ADq6upQrFRitr0DWRcvIuX1C9Dr9QcDQDgOx42TWFNnwZWbC1YsRltbG9beeBMM7UPhlcv4h6bR399/MAC8V37I5FkskNJ+EGUastRqeE1myHJyIC8ogOvIEdyQy8ARIrwJLRYLRkZGBJ9C3Z8WaDc2oM3Pw/rIryBiMZTP1YDxekEtLIBWpMDW0CAcYH5+HhMTE+CHy27CcVxkSkqlUqgVChxNTcOx5+tBdX+Nu5cu4djnn0FZWwuz2QzjTz8jx3YTHq0W93Q6YXNAcOrbFNnNTdhqaiF/shCFPT3weDzo7u6OaIgYBk+YTJirqDg4gNtvvY01gwFF31yBV6VCX18fAoGAkFyi54AQq+06IbcbthdfQmpdHe51tMNoNO7FRTSA2+2Gw+GARBJ/ReB7hL+W2XfehcjthuncuUjD7VGiAUwmE8bGxgT5OeR04sTwdSyXnIDj1ClBNg8oJT6K+UFU2XMZRCLB7+dfA/OQisWgSxwgb3wcR/92wHb6NDxaTSLZ8zaJASTRNCq+7cOGWg3ry02JBk8coOzqd1AEgzC9+gq/1z1egGyTGfkzM3BUPIu7hYWPEnzvFUh3OlH82wS8mRmwNTbGu2SEggnvAdn6OkqGhsElJcHc0gwuztouNHqkCe9MTYVzysu3Nklgt6WUD148MgJpOIzpFxrgPXxoDzHiqq6SWx98yBS9/56Ifzjw8iCAwuXCU2PjkHAc7DU1j3Lkdr+MbO3tbLFeT8jW2rwdIGfKBN3cHMJyeeRRsapJ+LzHKsMqsZ5p5pRlZchoPQ+xSgXHtWug+q8iecMLEcdiTaPGbFUVNpOT96vsO/wQ+xdfBjE5KWX9fvBV8LvdnNfnZb0ZGcyd0tKAX6lkDyQywPed5z/3UHufr8Z9OQAAAABJRU5ErkJggg=="
    print(saveFileToServer(testImg, 'anotherImg.png'))
    # print(deleteFileFromServer('/files.grimm-mueller.de/imageHost/anotherImg1.png'))

if __name__ == "__main__":
    main()