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

from bs4 import BeautifulSoup
import urllib2
import os
import ConfigParser
import datetime
import json

import mdb                  # Custom library for mongo interaction
import geojson              # Non-standard FOSS library
from baseObjects import *


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
        cwd = os.path.dirname(filePath)
        parent = os.path.dirname(cwd)
        
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
        
        self.tflDomain = config.get("default", "tflDomain")
        
        # Other parameters
        self.feedUrl = config.get("default", "url")
        
        self.logLevel  = self.checkLogLevel(config.get("error", "loglevel"))
        errorPath      = config.get("error", "err_path")   
        self.errorPath = os.path.join(parent, errorPath)
        self.errorFile = config.get("error", "err_file")
        self.webErrorFile = config.get("error", "web_err_file")
        
    def checkLogLevel(self, logLevel):
        ''' Checks that the log level is correct or defaults to DEBUG.'''
        
        logLevel = logLevel.upper()
        if logLevel in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            level = getattr(logging, logLevel)
        else:
            level = 10
        return level

#------------------------------------------------------------------------------------------ 
                
def hitFeed(feedUrl):
    ''' Hits the feed and gets back the rss xml file.
        Need some error handling in here. '''
    
    try:
        response = urllib2.urlopen(feedUrl)
    except:
        logging.error("Failed to connect to URL:%s" %(feedUrl), exc_info=True)
        
    try:
        content = response.read()
    except:
        logging.error("Failed to Extract content from feed data.", exc_info=True)
        content = None
    
    return content

#------------------------------------------------------------------------------------------

def extractContent(data):
    '''Builds a list of python dictionaries ready for insert/update.'''
    
    try:
        soup = BeautifulSoup(data, 'xml')
    except:
        logging.error("Failed to parse XML feed.", exc_info=True)
        soup, header, rootUrl, cameras = None, None, None, None
    
    if soup:
        try:
            header = soup.header
        except:
            logging.warning("Failed to get header from XML.", exc_info=True)
            header = None
        
        try:
            rootUrl = soup.cameraList.rooturl.contents[0]
        except:
            logging.warning("Failed to get root url for cams.", exc_info=True)
            rootUrl = None
            
        try:
            cameras = soup.findAll('camera')
        except:
            logging.warning("Failed to get camera tags.", exc_info=True)
            cameras = None
        
    return header, rootUrl, cameras

#------------------------------------------------------------------------------------------
    
    
def mongoInsert(collectionHandle, item):
    ''' Build the query condition: loc, camera name, camera number, link
        Build the $set - timestamp.
        This ensures that anything new gets inserted, anything old gets updated = a current db.'''
    
    # Export the item attributes to json
    doc = item.toJson()
    
    # Build the query part
    query = {'camId' : doc['camId']}
    
    # Build the update command
    command = {'loc'   : doc['loc'],
               'geo'   : doc['geo'],
               
               'feed'   : doc['feed'],
               'source' : doc['source'],
               'cprt'   : doc['cprt'],
               
               'title'    : doc['title'],
               'corridor' : doc['corridor'],
               'currView' : doc['currView'],
               'link'     : doc['link'],
               
               'inserted'  : doc['inserted'],
               'published' : doc['published'],
               'captured'  : doc['captured']
               
               }
    
    # Insert/update statement
    response = collectionHandle.update(query, {'$set':command}, True, False)
    #response = collectionHandle.insert(doc)


    