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
    
    def __init__(self, channel):
        ''' Handles the feed channel/top level feed information into an object.  '''
        
        self.errors = []
        self.channel = channel
        
        
        self.getFeedTitle()
        self.getFeedDescription()
        self.getFeedPubDate()
        self.getCopyright()
        self.getFeedLink()
    
    #-----------------------------------------------------------------------------

    def getFeedTitle(self):
        ''' Gets the feed title'''
        
        try:
            self.title = self.channel.title.contents[0].lower()
        except Exception, e:
            self.title = None
            self.errors.append(e)

    #-----------------------------------------------------------------------------

    def getFeedDescription(self):
        ''' Gets the feed description.'''

        try:
            self.description = self.channel.description.contents[0]
        except Exception, e:
            self.description = None
            self.errors.append(e)

    #-----------------------------------------------------------------------------

    def getFeedPubDate(self):
        ''' Gets the feed description.'''

        try:
            self.pubDate = self.getPubDate(self.channel.pubDate.contents[0])
        except Exception, e:
            self.pubDate = None
            self.errors.append(e)

    #-----------------------------------------------------------------------------

    def getCopyright(self):
        ''' Gets the feed feed copyright.'''
        
        try:
            self.copyright = self.channel.copyright.contents[0]
        except Exception, e:
            self.copyright = None
            self.errors.append(e)
        
    #-----------------------------------------------------------------------------

    def getFeedLink(self):
        ''' Gets the feed top level link.'''

        try:
            self.link = self.channel.link.contents[0]
        except Exception, e:
            self.link = None
            self.errors.append(e)
        
    #-------------------------------------------------------------------------------------

    def getPubDate(self, pubDate):
        ''' Gets the published date into a python datetime'''

        try:
            # Split the timezone from the main datetime
            dateComponents = pubDate.split(' ')
            pubDate = ' '.join(dateComponents[:-1])
            tz = dateComponents[-1]
            sign = tz[0]
            zone = tz[1:3]+'.'+tz[3:]
            if zone[0] == '0':
                zone = tz[2:3]+'.'+tz[3:]
            else:
                zone = tz[1:3]+'.'+tz[3:]
                
            # Apply the offset/timezoen to the datetime to get into UTC
            offset = datetime.timedelta(hours=float(zone))
            pubDate = datetime.datetime.strptime(pubDate, '%a, %d %b %Y %H:%M:%S')
        
            if sign == '+':
                pubDate += offset
            elif sign == '-':
                pubDate -= offset
            
            return pubDate
            
        except Exception, e:
            self.link = None
            self.errors.append(e)
                
#================================================================================================

class feedItem():
    ''' Makes an RSS item into an object for some modifications, access to params 
        and to export to json'''
    
    def __init__(self, feedChannel, item, source):
        
        #self.__init__ = feedChannel.__init__(fc)
        self.errors = []
        # Channel - top level feed attributes
        
        self.source          = source
        self.title           = feedChannel.title
        self.description     = feedChannel.description
        self.link            = feedChannel.link
        self.pubDate         = feedChannel.pubDate
        self.copyright       = feedChannel.copyright
        
        # New - item specific elements
        self.itemTitle       = self.getItemTitle(item)
        self.itemLink        = self.getItemLink(item)
        self.camId           = self.getId(self.itemLink)
        self.itemGeo         = self.getItemGeo(item)
        #self.itemDescription = self.getItemDescription(item)

        self.insertTime      = self.insertedTime()

#----------------------------------------------------------------------------------------

    def insertedTime(self):
        ''' Gets the current UTC d time.'''
        
        dt = datetime.datetime.utcnow()
        return dt
    
#----------------------------------------------------------------------------------------

    def getItemTitle(self, item):
        ''' Gets the title of the feed item in lower case.'''
        
        try:
            title = item.title.contents[0].lower()
        except Exception, e:
            self.errors.append(e)
            title = None
            
        return title

#------------------------------------------------------------------------------------------

    def getId(self, link):
        ''' Gets the id from the url link.'''

        # Ensure the link has made it through
        if link:
            try:
                link = link.split('/')
                camId = link[-1].strip('.jpg')
            except Exception, e:
                self.errors.append(e)
                camId = None
        else:
            self.errors.append("No link provided for extracting cam ID.")
            camId = None
            
        return camId
        
#------------------------------------------------------------------------------------------

    def getItemLink(self, item):
        ''' Gets the link to the image'''

        try:
            link = item.link.contents[0]
        except Exception, e:
            self.errors.append(e)
            link = None

        return link
#------------------------------------------------------------------------------------------
        
    def getItemDescription(self, item):
        ''' Gets the description for the item.'''

        try:
            description = item.description.contents[0]
        except Exception, e:
            self.errors.append(e)
            description = None

        return description        

#------------------------------------------------------------------------------------------
        
    def getItemGeo(self, item):
        ''' Gets the point geo information'''

        try:
            point = item.Point
        except Exception, e:
            self.errors.append(e)
            point = None

        # This is bad xml parsing because the xml is badly formatted
        if point:
            try:
                lat = float(point.lat.contents[0])
                lon = float(point.long.contents[0])
                loc = [lon, lat]
            except Exception, e:
                self.errors.append(e)
        else:
            loc = None

        return loc

    #------------------------------------------------------------------------------------------ 
    
    def getIsoDateTime(self):
        ''' Gets the datetime in iso format'''

        try:
            isoTime = self.insertTime.isoformat()
        except Exception, e:
            self.errors.append(e)
            isoTime = None
            
        return isoTime
        
    #------------------------------------------------------------------------------------------ 
    
    def buildGeoJson(self):
        ''' Puts the contents into a geojson format. Although this is duplication of content,
            it might allow for easy dumping out to the map while still maintaining ease of lookup
            (which isn't so simple if the whole doc was in geojson format)'''
        
        props = {'feed'  : self.title,
                 'title' : self.itemTitle,
                 'link'  : self.itemLink,
                 'camId'  :self.camId,
                #'desc'  : self.itemDescription,
                 'dt'    : self.getIsoDateTime(),
                 'cprt'  : self.copyright
                 }
        
        # The feature collection
        geoms = []
        
        # The geometry for this keyword/timestamp/mgrs
        p = geojson.Polygon(coordinates=self.itemGeo)
    
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

        doc = {'loc'   : self.itemGeo,
               'feed'  : self.title,
               'title' : self.itemTitle,
               'link'  : self.itemLink,
               'camId' : self.camId,
               #'desc' : self.itemDescription,
               'pubDt' : self.pubDate,
               'insDt' : self.insertTime,
               'cprt'  : self.copyright,
               'geo'   : self.geoJson
               }
        
        return doc