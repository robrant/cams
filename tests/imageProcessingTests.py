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
"""import imageProcessing

class Test(unittest.TestCase):


    def testCheckThumbnailBuild(self):
        ''' Tries to build a thumbnail from an image'''
        
        outDir = '.'
        inFileName = './testTrafficCamImage.jpg'
        
"""

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCheckThumbnailBuild']
    unittest.main()