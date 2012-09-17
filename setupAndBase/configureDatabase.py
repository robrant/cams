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

import mdb
import json
from pymongo import DESCENDING, ASCENDING
from baseUtils import getConfigParameters, handleErrors

class params():
    
    def __init__(self, port, host, adminUser, adminPass):
        
        self.mongoPort = int(port)
        self.mongoHost = host
        self.adminUser = adminUser
        self.adminPass = adminPass

#------------------------------------------------------------------------------------

def writeConfigFile(configFile, dotcloudParams):
    ''' Writes in the new host and port information for the mongo instance.'''

    fIn = open(configFile, 'r')
    tmpFileName = os.path.join(os.path.dirname(configFile),'tmp.tmp')
    fOut = open(tmpFileName, 'w')
    
    for line in fIn:
        if line.startswith('port'):
            fOut.write('port = %s \n' %dotcloudParams.mongoPort)
        elif line.startswith('host'):
            fOut.write('host = %s \n' %dotcloudParams.mongoHost)
        else:
            fOut.write(line)
    fOut.close()
    fIn.close()
    
    os.rename(tmpFileName, configFile)

#------------------------------------------------------------------------------------

def getEnvironment(path='/home/dotcloud/', file='environment.json'):
    ''' Get the environment from the environment dotcloud file'''
    
    # Open the environment.json
    f = open(os.path.join(path, file), 'r')
    data = json.loads(f.read())
    f.close()
    
    # Get some of the environment parameters
    port = data['DOTCLOUD_DATA_MONGODB_PORT']
    host = data['DOTCLOUD_DATA_MONGODB_HOST']
    adminUser = data['DOTCLOUD_DATA_MONGODB_LOGIN']
    adminPass = data['DOTCLOUD_DATA_MONGODB_PASSWORD']
    
    p = params(port, host, adminUser, adminPass)

    return p

#------------------------------------------------------------------------

def main(configFile=None):
    ''' Takes the dotcloud default admin privs, authorises on the db, 
        creates the user I've specified and returns. '''
    
    # Get the parameters that were set up by dotcloud
    dcParams = getEnvironment()
    print dcParams.mongoHost, dcParams.mongoPort, dcParams.adminUser, dcParams.adminPass
       
    # Authenticate on the admin db
    c, dbh = mdb.getHandle(host=dcParams.mongoHost, port=dcParams.mongoPort, db='admin')

    # Authentication of the administrator
    try:
        auth = dbh.authenticate(dcParams.adminUser, dcParams.adminPass)
        print "---- Admin authorisation: %s." %auth
        
    except Exception, e:
        print "Failed to authenticate with mongo db as admin."
        print e

    # Create a new user
    p = getConfigParameters(configFile)
    # Switch the database handle to that being used from the admin one
    dbh = c[p.db]
    success = dbh.add_user(p.dbUser, p.dbPassword)
    c.disconnect()
    
    try:
        # Authenticate on the admin db
        c, dbh = mdb.getHandle(host=dcParams.mongoHost, port=dcParams.mongoPort, db=p.db)
        auth = dbh.authenticate(p.dbUser, p.dbPassword)
    except Exception, e:
        print "Failed to authenticate with mongo db."
        print e
    
    # Write out the new information to the regular config file
    writeConfigFile(configFile, dcParams)
    
    mdb.close(c, dbh)
    
if __name__ == "__main__":

    # Command Line arguments
    configFile = sys.argv[1]
    
    # first argument is the config file path
    if not configFile:
        print 'no Config file provided. Exiting.'
        sys.exit()
    
    main(configFile)