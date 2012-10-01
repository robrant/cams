'''
Created on Sep 15, 2012

@author: brantinghamr
'''
import unittest
import os
import sys
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
import tflWorker
import baseObjects
from bs4 import BeautifulSoup
import baseUtils
import datetime

class Test(unittest.TestCase):


    def testFileComparison(self):
        ''' Check whether we can successfully match files by byte comparison.'''
        
        parent = os.getcwd()
        localDir      = os.path.join(parent, 'comparisons')
        imageFileName = os.path.join(parent, 'candidate/candidateImage.jpg')
        
        same = tflWorker.alreadyExists(localDir, imageFileName)
        self.assertTrue(same)

    def testExtractContent(self):
        ''' Test the extraction of top level elements from the feed'''
        
        parent   = os.getcwd()
        dataDir = os.path.join(parent, 'feedTestResources')
        fxml = open(os.path.join(dataDir, 'jamCamsv2.xml'), 'r')
        data = fxml.read()
        
        errors, header, rootUrl, cameras = baseUtils.extractContent(data)
        self.assertEquals(rootUrl, '/tfl/livetravelnews/trafficcams/cctv/')
        
        headerTruth = 'TfL Traffic Cameras'
        self.assertEquals(header.identifier.contents[0], headerTruth)
        

    def testfeedChannel(self):
        ''' Test the instantiation of the feedchannel object'''
        
        parent   = os.getcwd()
        dataDir = os.path.join(parent, 'feedTestResources')
        fxml = open(os.path.join(dataDir, 'jamCamsv2.xml'), 'r')
        data = fxml.read()
        errors, header, rootUrl, cameras = baseUtils.extractContent(data)
        fc = baseObjects.feedChannel(header)
        
        self.assertEquals(fc.title, 'tfl traffic cameras')
        truthDate = datetime.datetime(2012,10,1,20,15,20)
        self.assertEquals(fc.pubDate, truthDate)
        
        truth = 'transport for london'
        self.assertEquals(fc.copyright, truth)
        
    def testfeedItemFunctions(self):
        ''' Test the instantiation of each feed item (camera)'''
        
        parent   = os.getcwd()
        dataDir = os.path.join(parent, 'feedTestResources')
        fxml = open(os.path.join(dataDir, 'jamCamsv2.xml'), 'r')
        data = fxml.read()
        errors, header, rootUrl, cameras = baseUtils.extractContent(data)
        fc = baseObjects.feedChannel(header)
        
        fi = baseObjects.feedItem(fc, cameras[1], rootUrl)
        
        self.assertEquals(fi.source, 'transport for london')
        self.assertEquals(fi.title, 'tfl traffic cameras')
        self.assertEquals(fi.pubDate, datetime.datetime(2012,10,1,20,15,20))
        self.assertEquals(fi.copyright, 'transport for london')
        
        # New - item specific elements
        self.assertEquals(fi.camTitle, 'ram st/barchard st')
        self.assertEquals(fi.camCorridor, 'a205')
        self.assertEquals(fi.camLink, '/tfl/livetravelnews/trafficcams/cctv/0000102645.jpg')
        self.assertEquals(fi.camCurrentView, 'ram st n/b')
        self.assertEquals(fi.camId, '0000102645')
        self.assertAlmostEquals(fi.camGeo[0], -0.1920207, 4)
        self.assertAlmostEquals(fi.camGeo[1],  51.458282, 4)
        self.assertEquals(fi.camCaptureTime, datetime.datetime(2012,10,01,20,13,38))
    
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCheckThumbnailBuild']
    unittest.main()