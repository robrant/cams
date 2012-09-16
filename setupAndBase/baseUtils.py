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

from bs4 import BeautifulSoup
import urllib2
import os
import ConfigParser
import datetime
import json

import mdb                  # Custom library for mongo interaction
import geojson              # Non-standard FOSS library
from baseObjects import *


# Get the directory in which this was executed (current working dir)
cwd = os.getcwd()
wsDir = os.path.dirname(cwd)


class getConfigParameters():
    ''' Gets the configuration parameters into an object '''
    
    def __init__(self, filePath):
        
        config = ConfigParser.ConfigParser()
        try:
            config.read(filePath)
        except Exception, e:
            print "Failed to read the config file for twitter connection client."
            print e
        
        # Keep the location of the config file in the config file for mods on the fly
        self.configFile = filePath
        
        # Mongo parameters
        self.dbHost     = config.get("backend", "host")
        self.dbPort     = config.getint("backend", "port")
        self.db         = config.get("backend", "db")

        self.dbUser         = config.get("backend", "user")
        self.dbPassword     = config.get("backend", "password")
        
        # Collections and indexes
        self.collections    = json.loads(config.get("backend", "collections"))
        self.camsCollection = self.collections[0]['collection']

        self.dropCollection = config.getboolean("backend", "drop_collection")
        
        self.webStaticRoute = config.get("default", "webStaticRoute")
        self.baseUrl        = config.get("default", "baseUrl")
        self.imagesUrl      = config.get("default", "imagesUrl")
        
        # Other parameters
        self.feedUrl = config.get("default", "url")
        self.verbose = config.get("default", "verbose")
        
        
        
#-------------------------------------------------------------------------------------

def handleErrors(errors, verbose=None):
    ''' Handles the printing (or other) of errors. '''

    # Report out the parsing errors if verbose is set
    if verbose and len(errors) != 0:
        print "="*10+"ERRORS FOUND"+"="*10
        for error in errors:
            print "-"*10+"Error"+"-"*10
            print error
            
#------------------------------------------------------------------------------------------ 
                
def hitFakeFeed(path, fileName):
    ''' Hits the feed and gets back the rss xml file.
        Need some error handling in here. '''

    errors = []

    try:
        fPath = os.path.join(path, fileName)
        f = open(fPath, 'r')
        data = f.read()
    except Exception, e:
        errors.append(e)
        
    return errors, data

#------------------------------------------------------------------------------------------ 
                
def hitFeed(feedUrl):
    ''' Hits the feed and gets back the rss xml file.
        Need some error handling in here. '''
    
    errors = []
    
    try:
        response = urllib2.urlopen(feedUrl)
    except Exception, e:
        errors.append(e)
        
    try:
        content = response.read()
    except Exception, e:
        errors.append(e)
        
    return errors, content
#------------------------------------------------------------------------------------------

def extractContent(data):
    '''Builds a list of python dictionaries ready for insert/update.'''
    
    # Gather up any errors
    errors = []
    
    try:
        soup = BeautifulSoup(data, 'xml')
    except Exception, e:
        errors.append(e)
        soup = None
        channel, items = None, None
    
    if soup:
        try:
            channel = soup.channel
        except Exception, e:
            errors.append(e)
            channel = None
            
        try:
            items = soup.findAll('item')
        except Exception, e:
            errors.append(e)
            items = None
        
    return errors, channel, items

#------------------------------------------------------------------------------------------
    
    
def mongoInsert(collectionHandle, item):
    ''' Build the query condition: loc, camera name, camera number, link
        Build the $set - timestamp.
        This ensures that anything new gets inserted, anything old gets updated = a current db.'''
    
    # Export the item attributes to json
    doc = item.toJson()
    
    # Build the query part
    query = {'title' : doc['title']}
    
    # Build the update command
    command = {'loc'   : doc['loc'],
               'link'  : doc['link'],
               'feed'  : doc['feed'],
               #'desc' : doc['desc'],
               'insDt' : doc['insDt'],
               'pubDt' : doc['pubDt'],
               'camId' : doc['camId'],
               'cprt'  : doc['cprt'],
               'geo'   : doc['geo']
               }
    
    # Insert/update statement
    response = collectionHandle.update(query, {'$set':command}, True, False)
    #response = collectionHandle.insert(doc)


    