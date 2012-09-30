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

class Test(unittest.TestCase):


    def testFileComparison(self):
        ''' Check whether we can successfully match files by byte comparison.'''
        
        parent = os.getcwd()
        localDir      = os.path.join(parent, 'comparisons')
        imageFileName = os.path.join(parent, 'candidate/candidateImage.jpg')
        
        same = tflWorker.alreadyExists(localDir, imageFileName)
        self.assertTrue(same)

        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCheckThumbnailBuild']
    unittest.main()