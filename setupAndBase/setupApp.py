import os
import sys
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
            sys.path.append(directory)

#============================================================================================

import configureDatabase
import setupDatabase
import baseUtils

# Get the config file
configFile = sys.argv[1]

# Where this is being run - 
site = sys.argv[2]

p = baseUtils.getConfigParameters(configFile)

# Setup the error logging
logFile = os.path.join(p.errorPath, p.errorFile)
logging.basicConfig(filename=logFile, format='%(levelname)s:: \t%(asctime)s %(message)s', level='DEBUG')

# Configuring the dotcloud settings for mongodb
if site == 'dotcloud':
    configureDatabase.main(configFile)
elif site == 'local':
    pass

# Setup the database
print '---- Setting up and populating database'
setupDatabase.main(configFile)

