import sys
import os
import logging
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

import mdb                  # Custom library for mongo interaction
import geojson              # Non-standard FOSS library
from baseObjects import feedItem, feedChannel
from baseUtils import getConfigParameters, hitFeed, extractContent, mongoInsert

"""
Description:
============
Retrieves and upserts Transport For London Traffic Camera location information into Mongo.
In doing so, makes the camera location and link to latest image available through spatial query.

To Do:
======
3. Bring in other datasets - other cctv locations around london.

"""

#------------------------------------------------------------------------------------------ 

def main():
    ''' '''
    
    # Connect and get db and collection handle
    try:
        c, dbh = mdb.getHandle(p.dbHost, p.dbPort, p.db, p.dbUser, p.dbPassword)
        collectionHandle = dbh[p.camsCollection]
    except:
        logging.critical("DB connection Failed", exc_info=True)
        
    # Get the feed content
    feedContent = hitFeed(p.feedUrl)
    if not feedContent:
        logging.critical("** SCRIPT EXIT **\n%s\n\n" %('='*52))
        sys.exit()
        
    # Break out the content into head and items
    header, rootUrl, cameras = extractContent(feedContent)
    if not header or not rootUrl or not cameras:
        logging.critical("** SCRIPT EXIT **\n%s\n\n" %('='*52))
        sys.exit()
    
    # Build the camera root URL    
    rootUrl = p.tflDomain + rootUrl   
    fc = feedChannel(header)
            
        # Deal with each of the items
    for camera in cameras:

        # Build an 'item' object based on the RSS item        
        item = feedItem(fc, camera, rootUrl)
        item.buildGeoJson()
        
        # Insert the document into mongo
        response = mongoInsert(collectionHandle, item)
        
#------------------------------------------------------------------------------------------

if __name__ == "__main__":

    # Command Line arguments
    configFile = sys.argv[1]
    
    # first argument is the config file path
    if not configFile:
        print 'no Config file provided. Exiting.'
        sys.exit()
    
    p = getConfigParameters(configFile)

    # Setup the error logging
    logFile = os.path.join(p.errorPath, p.errorFile)
    logging.basicConfig(filename=logFile, format='%(levelname)s:: \t%(asctime)s %(message)s', level=p.logLevel)
    
    main()
    
