import sys
import os
#============================================================================================
# TO ENSURE ALL OF THE FILES CAN SEE ONE ANOTHER.

# Get the directory in which this was executed (current working dir)
cwd = os.getcwd()
print cwd
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
from bottle import route, run, request, abort, error, static_file
import json
import tflWorker
import bottle
from baseUtils import getConfigParameters

bottle.debug(True)

os.chdir('/home/dotcloud/code/')
cwd = os.getcwd()
cfgs = os.path.join(cwd, 'config/tfl.cfg')
p = getConfigParameters(cfgs)

#------------------------------------------------------------------------------------
@route('/test', method='GET')
def get_test():
    return json.dumps({'hello':'foobar'})

#------------------------------------------------------------------------------------
@route('/images/<imageId>', method='GET')
def getThumbnail(imageId):
    ''' Gets the tfl cameras that were within a certain location '''

    return static_file(imageId, root=os.path.join(p.webStaticRoute, 'images'))

#------------------------------------------------------------------------------------------------

@route('/help')
def helpPage():
    ''' Will eventually render some help. '''

    #output = template("help")    
    return "help coming soon."
 
#------------------------------------------------------------------------------------
@route('/tfl', method='GET')
def get_tflCams():
    ''' Gets the tfl cameras that were within a certain location '''

    # Where to stage and store the full res and thumbnail
    imageDir = os.path.join(p.webStaticRoute, 'images')

    # Parse out the geo parameters
    lat, lon, radius = tflWorker.checkGeos(request.query.lat, request.query.lon, request.query.radius)
    
    if not lat or not lon or not radius:
        res = {'code':500, 'reason': 'lat/lon/radius not within bounds.'}
        return json.dumps(res)
    
    # Get the documents that fall within the search radius
    cameras = tflWorker.getCamsByGeo(p, lat, lon, radius)
    
    mediaOut = []
    
    if cameras:
        for camera in cameras:

            # Get the iamge dt for writing unique image files
            if camera['captured'] != None:
                dt = camera['captured'].strftime('%y%m%d%H%M%S') 
            else:
                dt = camera['published'].strftime('%y%m%d%H%M%S')
            
            # Build output json
            camMedia, reason = tflWorker.formatOutput(p, camera)
            if not camMedia:
                return json.dumps({'code':500, 'reason': "Failed to format the camera metadata."})
            
            # Create a local version of the TFL image for thumbnail and scaled up images
            localFile, reason = tflWorker.getFullRes(p, imageDir, camMedia['standard_resolution'], dt)

            # Do a byte-based comparison to see whether this image already exists in the originals/ directory
            dupe = tflWorker.alreadyExists(imageDir, localFile)
            
            # Remove the one we've just pulled down
            if dupe:
                out, reason = tflWorker.removeFullRes(localFile)
                continue
            
            if not localFile:
                return json.dumps({'code':500, 'reason': "Failed to get the full resolution image."})
            largeFile, reason = tflWorker.createLargerImage(imageDir, localFile, scale=1.2)
            
            # Build a thumbnail
            imageThumb, reason = tflWorker.createThumbnail(imageDir, localFile, size=100)
            if not imageThumb:
                return json.dumps({'code':500, 'reason': "Failed to create the thumbnail."})
            
            #out, reason = tflWorker.removeFullRes(localFile)
            camMedia['thumbnail']           = tflWorker.assignLocalCopies(p, imageThumb)
            camMedia['standard_resolution'] = tflWorker.assignLocalCopies(p, largeFile)
            camMedia['low_resolution']      = tflWorker.assignLocalCopies(p, largeFile)

            mediaOut.append(camMedia)
            
    else:
        mediaOut = []
    
    return json.dumps(mediaOut)
    
    
    
    
    
 
    
