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
import logging
import mdb                  # Custom library for mongo interaction
import geojson              # Non-standard FOSS library

#================================================================================================

class feedChannel(object):
    '''    '''
    
    def __init__(self, header):
        ''' Handles the feed channel/top level feed information into an object.  '''
        
        self.header = header
        
        self.getFeedTitle()
        self.getFeedPubDate()
        self.getCopyright()
    
    #-----------------------------------------------------------------------------

    def getFeedTitle(self):
        ''' Gets the feed title'''
        
        try:
            self.title = self.header.identifier.contents[0].lower()
        except:
            self.title = None
            logging.critical("Failed to get the feed title.", exc_info=True)
        
    #-----------------------------------------------------------------------------

    def getFeedPubDate(self):
        ''' Gets the feed description.'''

        try:
            pd = self.header.publishDateTime.contents[0]
            self.pubDate = self.getPubDate(pd)
        except:
            self.pubDate = None
            logging.error("Failed to get the feed pub date.", exc_info=True)

    #-----------------------------------------------------------------------------

    def getCopyright(self):
        ''' Gets the feed feed copyright.'''
        
        try:
            self.copyright = self.header.owner.contents[0].lower()
        except:
            logging.warning("Failed to get copyright info.", exc_info=True)
            self.copyright = 'tfl'
        
    #-------------------------------------------------------------------------------------

    def getPubDate(self, pubDate):
        ''' Gets the published date into a python datetime'''

        try:
            pubDate = datetime.datetime.strptime(pubDate, "%Y-%m-%dT%H:%M:%SZ")
        except:
            logging.warning("Failed to strip datetime: %s." %(pubDate), exc_info=True)
            pubDate = None
            
        return pubDate
                
#================================================================================================

class feedItem():
    ''' Makes an RSS item into an object for some modifications, access to params 
        and to export to json'''
    
    def __init__(self, feedChannel, camera, rootUrl):
        
        #self.__init__ = feedChannel.__init__(fc)
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
        except:
            logging.info("Failed to get camera title info", exc_info=True)
            title = None
            
        return title

#----------------------------------------------------------------------------------------

    def getCamCorridor(self, camera):
        ''' Gets the traffic corridor in question.'''
        
        try:
            corridor = camera.corridor.contents[0].lower()
        except:
            logging.info("Failed to get corridor info", exc_info=True)
            corridor = None
            
        return corridor
    
#------------------------------------------------------------------------------------------

    def getCamId(self, camera):
        ''' Gets the id from the url link.'''

        try:
            fileId = camera.file.contents[0]
            camId = fileId.split('.')[0]
        except:
            logging.info("Failed to Cam ID", exc_info=True)
            camId = None
            
        return camId
        
#------------------------------------------------------------------------------------------

    def getCamLink(self, rootUrl, camera):
        ''' Gets the link to the image'''

        try:
            imageFile = camera.file.contents[0]
            link = rootUrl + imageFile
        except:
            logging.info("Failed to get image URL", exc_info=True)
            link = None

        return link
#------------------------------------------------------------------------------------------
        
    def getCamDescription(self, camera):
        ''' Gets the description for the item.'''

        try:
            description = camera.currentView.contents[0].lower()
        except:
            logging.info("Failed to get image description.", exc_info=True)
            description = None

        return description        

#------------------------------------------------------------------------------------------
        
    def getCamGeo(self, camera):
        ''' Gets the point geo information'''

        try:
            lat = float(camera.lat.contents[0])
        except:
            lat = None
            logging.info("Failed to get camera Lat.", exc_info=True)
        
        try:
            lon = float(camera.lng.contents[0])
        except:
            lon = None
            logging.info("Failed to get camera Lon.", exc_info=True)


        return [lon, lat]

    #------------------------------------------------------------------------------------------ 

    def getCamCapture(self, camera):
        ''' Get the camera capture datetime group'''

        try:
            captureTime = camera.captureTime.contents[0]
            captured = datetime.datetime.strptime(captureTime, "%Y-%m-%dT%H:%M:%SZ")
            
        except:
            captured = datetime.datetime(1970,1,1)
            logging.info("Failed to get camera capture time. Set to default unix epoch.", exc_info=True)
            
        return captured

    #------------------------------------------------------------------------------------------ 
    
    def getIsoDateTime(self):
        ''' Gets the datetime in iso format'''

        try:
            isoTime = self.insertTime
        except:
            logging.info("Failed to get inser time.", exc_info=True)
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