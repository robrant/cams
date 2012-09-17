import sys
import os
#============================================================================================
# TO ENSURE ALL OF THE FILES CAN SEE ONE ANOTHER.

# Get the directory in which this was executed (current working dir)
cwd = os.getcwd()
wsDir = os.path.dirname(cwd)

# Find out whats in this directory recursively
for root, subFolders, files in os.walk(wsDir):
    # Loop the folders listed in this directory
    for folder in subFolders:
        directory = os.path.join(root, folder)
        if directory.find('.git') == -1:
            if directory not in sys.path:
                sys.path.append(directory)

#============================================================================================
import mdb
import urllib2
import Image
import math
from pymongo.son import SON

def checkGeos(lat=None, lon=None, radius=None, maxRad=5000.0):
    ''' Checks the validity of lat, lon and radius '''

    try:    lat = float(lat)
    except: lat = None
    try:    lon = float(lon)
    except: lon = None
    try:    radius = float(radius)
    except: radius = None

    if not lat or lat < -90.0 or lat > 90.0:
        lat = None
    
    if not lon or lon < -180.0 or lon > 180.0:
        lon = None

    if radius < 0.0 or radius > maxRad:
        radius = None
        
    return lat, lon, radius

#--------------------------------------------------------------------------------------------

def radialToLinearUnits(latitude):
    
    ''' Calculates the length of 1 degree of latitude and longitude at
        a given latitude. Takes as arguments the latitude being worked at.
        Returns the length of 1 degree in metres. NEEDS TESTING '''
    
    # Work in radians
    lat = math.radians(latitude)
    
    # Constants
    m1 = 111132.92
    m2 = -559.82
    m3 = 1.175
    m4 = -0.0023
    p1 = 111412.84
    p2 = -93.5
    p3 = 0.118
    
    # Length of a degree in Latitude
    latLen = m1 + (m2 * math.cos(2 * lat)) + (m3 * math.cos(4 * lat)) + \
             (m4 * math.cos(5 * lat))
             
    lonLen = (p1 * math.cos(lat)) + (p2 * math.cos(3*lat)) + (p3 * math.cos(5*lat))
        
    return latLen, lonLen

#--------------------------------------------------------------------------------------------

def getCamsByGeo(p, lat, lon, radius, postcode=None):
    '''Get the cameras that fall within radius of lat/lon or postcode'''
    
    # The mongo bits
    c, dbh = mdb.getHandle(host=p.dbHost, port=p.dbPort, db=p.db, user=p.dbUser, password=p.dbPassword)
    camsCollHandle = dbh[p.camsCollection] 
    
    # Convert the incoming metres radius to degrees
    latRad, lonRad = radialToLinearUnits(lat)
    scale = (latRad+lonRad)/2.0
    radius = float(radius)/scale
    
    # Query mongo
    query = SON({'$near':[float(lon), float(lat)]})
    query['$maxDistance'] = radius
    res = camsCollHandle.find({'loc' : query})
    
    # Get results
    if res:
        results = [r for r in res]
    if len(results) == 0:
        results = None
        
    return results
    
#--------------------------------------------------------------------------------------------

def formatOutput(p, camRecord):
    '''Format the camera records into the format for crowded.'''
    
    cam = None
    try:
        cam = {"caption" : camRecord['title'],
               "dt"      : camRecord['insDt'].isoformat(),
               "source"  : camRecord['cprt'],
               "loc"     : camRecord['loc']}
        reason = None
    except Exception, e:
        reason = e
        
        print "Failed to get camera metadata from tfl."
    
    try:
        cam['low_resolution']      = camRecord['link']
        cam['standard_resolution'] = camRecord['link']
        cam['thumbnail'] = None
        reason = None
    except Exception, e:
        cam = None
        reason = e
        print "Failed to get camera image links."
        
    return cam, reason

#--------------------------------------------------------------------------------------------
def assignLocalCopies(p, localFile):
    ''' Changes the output dictionary to reflect the locally help image file.'''

    fileName = localFile.split('/')[-1]
    fileUrl = p.imagesUrl+fileName
    return fileUrl

#--------------------------------------------------------------------------------------------
def getFullRes(p, tempDir, fileUrl, dt):
    ''' Gets the file back from the tfl webserver'''
    
    try:
        imageData = urllib2.urlopen(fileUrl).read()
    except Exception, e:
        print "Failed to read image data from source URL: %s" %(fileUrl)
        return None, e
    
    try:
        fileName = "%s_%s" %(dt, fileUrl.split('/')[-1])
        fullPath = os.path.join(tempDir, fileName)
        print "Output image filename %s" %fileName
        f = open(fullPath, 'w')
        print "Output image fullpath %s" %fullPath
        f.write(imageData)
        f.close()
        reason = None
    except Exception, e:
        fullPath, reason = None, e
        print "Failed to write the image content to the local directory."
    
    return fullPath, reason

#--------------------------------------------------------------------------------------------

def removeFullRes(localFile):
    ''' Removes the local full size file.'''

    try:
        os.remove(localFile)
        out, reason = 1, None
    except Exception, e:
        out, reason = None, e

    return out, reason

#--------------------------------------------------------------------------------------------

def createLargerImage(inFilePath, scale=1.2):
    ''' Enlarges the incoming image'''
    
    try:
        # Get the file name for the thumbnail
        root, ext = os.path.splitext(inFilePath) 
        large =  "%s_large%s" %(root, ext)  
        # Set the size of the thumbnail
        
        im = Image.open(inFilePath)
        currentSize = im.size
        im = im.resize((currentSize[0]*scale, currentSize[1]*scale))
        im.save(large, "JPEG")
        out = large.split('/')[-1]
        reason = None 
    except Exception, e:
        print e
        out, reason = None, e
    
    return out, reason
    
#--------------------------------------------------------------------------------------------

def createThumbnail(inFilePath, size=50):
    ''' Creates a thumbnail per image and saves it out'''
    
    try:
        # Get the file name for the thumbnail
        root, ext = os.path.splitext(inFilePath) 
        thumb =  "%s_thumb%s" %(root, ext)  
        # Set the size of the thumbnail
        thumbSize = size, size 
        
        im = Image.open(inFilePath)
        im.thumbnail(thumbSize)
        im.save(thumb, "JPEG")
        out = thumb.split('/')[-1]
        reason = None 
    except Exception, e:
        out, reason = None, e
    
    return out, reason

#--------------------------------------------------------------------------------------------

