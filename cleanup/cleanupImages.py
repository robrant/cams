import sys

import os
import datetime

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
                os.remove(candidate)
        
    else:
        print "Directory doesn't exist. No file cleaning/aging will take place."
    
if __name__ == "__main__":

    # Command Line arguments
    try:
        directory = sys.argv[1]
    except:
        print; print "*"*68
        print 'Provide the top level path in which to check for old files. '
        print "*"*68; print
        sys.exit(1)

    try:
        lookback = sys.argv[2]
    except:
        lookback = None
    
    main(directory, lookback)