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
import datetime

import mdb                  # Custom library for mongo interaction
import geojson              # Non-standard FOSS library

#================================================================================================

class feedChannel(object):
    '''    '''
    
    def __init__(self, header):
        ''' Handles the feed channel/top level feed information into an object.  '''
        
        self.errors = []
        self.header = header
        
        self.getFeedTitle()
        self.getFeedPubDate()
        self.getCopyright()
    
    #-----------------------------------------------------------------------------

    def getFeedTitle(self):
        ''' Gets the feed title'''
        
        try:
            self.title = self.header.identifier.contents[0].lower()
        except Exception, e:
            self.title = None
            self.errors.append(e)

    #-----------------------------------------------------------------------------

    def getFeedPubDate(self):
        ''' Gets the feed description.'''

        try:
            pd = self.header.publishDateTime.contents[0]
            self.pubDate = self.getPubDate(pd)
            
        except Exception, e:
            self.pubDate = None
            self.errors.append(e)

    #-----------------------------------------------------------------------------

    def getCopyright(self):
        ''' Gets the feed feed copyright.'''
        
        try:
            self.copyright = self.header.owner.contents[0].lower()
        except Exception, e:
            self.copyright = None
            self.errors.append(e)
        
    #-------------------------------------------------------------------------------------

    def getPubDate(self, pubDate):
        ''' Gets the published date into a python datetime'''

        #try:
        pubDate = datetime.datetime.strptime(pubDate, "%Y-%m-%dT%H:%M:%SZ")
            
        #except Exception, e:
        #    self.errors.append(e)

        return pubDate
                
#================================================================================================

class feedItem():
    ''' Makes an RSS item into an object for some modifications, access to params 
        and to export to json'''
    
    def __init__(self, feedChannel, camera, rootUrl):
        
        #self.__init__ = feedChannel.__init__(fc)
        self.errors = []
        # Channel - top level feed attributes
        
        self.source          = feedChannel.copyright
        self.title           = feedChannel.title
        self.pubDate         = feedChannel.pubDate
        self.copyright       = feedChannel.copyright
        
        # New - item specific elements
        self.camTitle       = self.getCamTitle(camera)
        self.camCorridor    = self.getCamCorridor(camera)
        self.camLink        = self.getCamLink(rootUrl, camera)
        self.camCurrentView = self.getCamDescription(camera)
        self.camId          = self.getCamId(camera)
        self.camGeo         = self.getCamGeo(camera)
        self.camCaptureTime = self.getCamCapture(camera)
        
        self.insertTime      = self.insertedTime()

#----------------------------------------------------------------------------------------

    def insertedTime(self):
        ''' Gets the current UTC d time.'''
        
        dt = datetime.datetime.utcnow()
        return dt
    
#----------------------------------------------------------------------------------------

    def getCamTitle(self, camera):
        ''' Gets the title of the feed item in lower case.'''
        
        try:
            title = camera.location.contents[0].lower()
        except Exception, e:
            self.errors.append(e)
            title = None
            
        return title

#----------------------------------------------------------------------------------------

    def getCamCorridor(self, camera):
        ''' Gets the traffic corridor in question.'''
        
        try:
            corridor = camera.corridor.contents[0].lower()
        except Exception, e:
            self.errors.append(e)
            corridor = None
            
        return corridor
    
#------------------------------------------------------------------------------------------

    def getCamId(self, camera):
        ''' Gets the id from the url link.'''

        try:
            fileId = camera.file.contents[0]
            camId = fileId.split('.')[0]
        except Exception, e:
            self.errors.append(e)
            camId = None
            
        return camId
        
#------------------------------------------------------------------------------------------

    def getCamLink(self, rootUrl, camera):
        ''' Gets the link to the image'''

        try:
            imageFile = camera.file.contents[0]
            link = rootUrl + imageFile
        except Exception, e:
            self.errors.append(e)
            link = None

        return link
#------------------------------------------------------------------------------------------
        
    def getCamDescription(self, camera):
        ''' Gets the description for the item.'''

        try:
            description = camera.currentView.contents[0].lower()
        except Exception, e:
            self.errors.append(e)
            description = None

        return description        

#------------------------------------------------------------------------------------------
        
    def getCamGeo(self, camera):
        ''' Gets the point geo information'''

        try:
            lat = float(camera.lat.contents[0])
        except Exception, e:
            lat = None
            self.errors.append(e)
        
        try:
            lon = float(camera.lng.contents[0])
        except Exception, e:
            lon = None
            self.errors.append(e)

        return [lon, lat]

    #------------------------------------------------------------------------------------------ 

    def getCamCapture(self, camera):
        ''' Get the camera capture datetime group'''

        try:
            captureTime = camera.captureTime.contents[0]
            captured = datetime.datetime.strptime(captureTime, "%Y-%m-%dT%H:%M:%SZ")
            
        except Exception, e:
            captured = datetime.datetime(1970,1,1)
            self.errors.append(e)
            
        return captured

    #------------------------------------------------------------------------------------------ 
    
    def getIsoDateTime(self):
        ''' Gets the datetime in iso format'''

        try:
            isoTime = self.insertTime
        except Exception, e:
            self.errors.append(e)
            isoTime = datetime.datetime(1970,1,1)

            
        return isoTime
        
    #------------------------------------------------------------------------------------------ 
    
    def buildGeoJson(self):
        ''' Puts the contents into a geojson format. Although this is duplication of content,
            it might allow for easy dumping out to the map while still maintaining ease of lookup
            (which isn't so simple if the whole doc was in geojson format)'''
        
        props = {'feed'  : self.title,
                 'source': self.source,
                 'cprt'  : self.copyright,
  
                 'title'    : self.camTitle,
                 'corridor' : self.camCorridor,
                 'currView' : self.camCurrentView,
                 'link'     : self.camLink,
                 'camId'    : self.camId,

                 'inserted'  : self.insertTime.isoformat(),
                 'published' : self.pubDate.isoformat(),
                 'captured'  : self.camCaptureTime.isoformat()}
        
        # The feature collection
        geoms = []
        
        # The geometry for this keyword/timestamp/mgrs
        p = geojson.Polygon(coordinates=self.camGeo)
    
        geom = geojson.feature.Feature(id=self.camId,
                                       geometry=p,
                                       properties=props)
        
        geoms.append(geom)
        collection = geojson.feature.FeatureCollection(features=geoms)
        
        # Return the geojson doc as a dictionary
        geoJson = geojson.dumps(collection)
        self.geoJson = geojson.loads(geoJson)
        
#------------------------------------------------------------------------------------------

    def toJson(self):
        ''' Reformats the item attributes to json for mongo insert/update'''

        doc = {'loc'   : self.camGeo,
               'geo'   : self.geoJson,
               
               'feed'  : self.title,
               'source': self.source,
               'cprt'  : self.copyright,

               'title'    : self.camTitle,
               'corridor' : self.camCorridor,
               'currView' : self.camCurrentView,
               'link'     : self.camLink,
               'camId'    : self.camId,

               'inserted'  : self.insertTime,
               'published' : self.pubDate,
               'captured'  : self.camCaptureTime
               }
        
        return doc