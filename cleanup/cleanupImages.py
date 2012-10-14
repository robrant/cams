import sys
import logging
import os
import datetime
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
import baseUtils

def getLookBack(hours):
    '''Gets a time delta object'''

    secs = float(hours) * 60 * 60
    lb = datetime.timedelta(seconds=secs)
    return lb

def main(directory, lookback=3, fileType='jpg'):
    ''' Deletes files from the 'directory' and descends recursively if instructed.'''
    
    # Get the period before which the files will be removed
    lookback = getLookBack(lookback)
    cutOff = datetime.datetime.now() - lookback
    
    # Check it exists
    if os.path.exists(directory):
        
        # Loop the files in this directory
        for filex in os.listdir(directory):
            
            # Get the modified time and that into a python datetime
            candidate = os.path.join(directory, filex)
            modTime = os.path.getmtime(candidate)
            modDateTime = datetime.datetime.fromtimestamp(modTime)
            
            # Remove it if its old
            if modDateTime < cutOff and candidate.endswith(fileType):
                try:
                    os.remove(candidate)
                except:
                    logging.info("Failed to remove file: %s" %(candidate), exc_info=True)

    else:
        logging.info("Directory (%s) doesn't exist. No file cleaning/aging will take place." %(directory))

    
if __name__ == "__main__":

    # Command Line arguments
    configFile = sys.argv[1]
    
    # first argument is the config file path
    if not configFile:
        print 'no Config file provided. Exiting.'
        sys.exit()
    
    p = baseUtils.getConfigParameters(configFile)

    # Setup the error logging
    logFile = os.path.join(p.errorPath, p.errorFile)
    logging.basicConfig(filename=logFile, format='%(levelname)s:: \t%(asctime)s %(message)s', level=p.logLevel)

    # Command Line arguments
    try:
        directory = sys.argv[2]
    except:
        logging.info("Failed to get the directory to clean. Pls provide as argument.")
        sys.exit()

    try:
        lookback = sys.argv[3]
    except:
        lookback = None
    
    main(directory, lookback)
    