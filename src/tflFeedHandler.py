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

import mdb                  # Custom library for mongo interaction
import geojson              # Non-standard FOSS library
from baseObjects import *
from baseUtils import getConfigParameters, hitFeed, extractContent, handleErrors, feedItem, feedChannel, mongoInsert

"""
Description:
============
Retrieves and upserts Transport For London Traffic Camera location information into Mongo.
In doing so, makes the camera location and link to latest image available through spatial query.

To Do:
======
1. Write some example queries using $near operator
2. Check that the indexes are suitable
3. Bring in other datasets - other cctv locations around london.



"""
os.chdir('/home/dotcloud/code/')
cwd = os.getcwd()
cfgs = os.path.join(cwd, 'config/tfl.cfg')
p = getConfigParameters(cfgs)


#------------------------------------------------------------------------------------------ 

def main():
    ''' '''
    
    # Connect and get db and collection handle
    c, dbh = mdb.getHandle(p.dbHost, p.dbPort, p.db)
    collectionHandle = dbh[p.camsCollection]
    
    # Authentication
    auth = dbh.authenticate(p.dbUser, p.dbPassword)
    
    # Get the feed content
    errors, feedContent = hitFeed(p.feedUrl)
    #errors, feedContent = hitFakeFeed(pathIn, fakeFeedFile)

    # Break out the content into head and items
    extractErrors, channel, items = extractContent(feedContent)
    errors += extractErrors

    if p.verbose and len(errors) != 0:
        handleErrors(errors)
        sys.exit()
        
    fc = feedChannel(channel)
    
    # Check for errors on the feed channel read
    if p.verbose and len(fc.errors) != 0:
        handleErrors(errors)
        sys.exit()
        
        # Deal with each of the items
    for itemXml in items:

        # Build an 'item' object based on the RSS item        
        item = feedItem(fc, itemXml, 'tfl')
        if p.verbose and len(item.errors) != 0:
            handleErrors(errors)
        
        item.buildGeoJson()
        
        # Insert the document into mongo
        response = mongoInsert(collectionHandle, item)
        
#------------------------------------------------------------------------------------------

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testConnection']
    main()