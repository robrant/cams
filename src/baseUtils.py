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

    
    