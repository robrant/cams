#! /usr/bin/python

import sys
importDir = ['/Users/brantinghamr/Documents/Code/eclipseWorkspace/bam/src/tests/',
             '/Users/brantinghamr/Documents/Code/eclipseWorkspace/bam/src/scripts/',
             '/Users/brantinghamr/Documents/Code/eclipseWorkspace/bam/src/libs/']
for dirx in importDir:
    if dirx not in sys.path: sys.path.append(dirx)

from bs4 import BeautifulSoup
import urllib2
import os
import ConfigParser
import datetime

import mdb                  # Custom library for mongo interaction
import geojson              # Non-standard FOSS library
from baseObjects import *
from baseUtils import * 

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


#------------------------------------------------------------------------------------------ 

def main():
    ''' '''
    # Config file parameters
    pathIn = '/Users/brantinghamr/Documents/Code/eclipseWorkspace/bam/src/tflCode/'
    fileIn = 'tfl.cfg'
    fakeFeedFile = 'tflTrafficCamLocations.xml'
    
    # Get parameters from config
    p = params(pathIn, fileIn)
    
    # Connect and get db and collection handle
    c, dbh = mdb.getHandle(p.host, p.port, p.db)
    collectionHandle = dbh[p.coll]
    
    # Authentication
    auth = dbh.authenticate(p.user, p.password)
    print auth
    
    # Get the feed content
    #feedContent = hitFeed(p.feedUrl)
    errors, feedContent = hitFakeFeed(pathIn, fakeFeedFile)

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
        item = feedItem(fc, itemXml)
        if p.verbose and len(item.errors) != 0:
            handleErrors(errors)
        
        item.buildGeoJson()
        
        # Insert the document into mongo
        response = mongoInsert(collectionHandle, item)
        print response
        
#------------------------------------------------------------------------------------------

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testConnection']
    main()