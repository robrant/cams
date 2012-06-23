import sys

importDir = ['/Users/brantinghamr/Documents/Code/eclipseWorkspace/bam/src/tests/',
             '/Users/brantinghamr/Documents/Code/eclipseWorkspace/bam/src/scripts/',
             '/Users/brantinghamr/Documents/Code/eclipseWorkspace/bam/src/libs/']
for dirx in importDir:
    if dirx not in sys.path: sys.path.append(dirx) 

import mdb
from pymongo import GEO2D, ASCENDING, DESCENDING

#------------------------------------------------------------------------

def main():
    ''' Builds the collections and indexes needed for the bam mongo work.
        # See also /src/tests/testMdb for full tests of the base functions. '''
    
    db = 'tfl'
    host = 'localhost'
    port = 27017
    collection = 'locs'
    
    # Get a db handle
    print "Get Mongo Handle."
    c, dbh = mdb.getHandle(host=host, port=port, db=db)
    
    # Create the collection
    try:
        dbh.create_collection(collection)
    except:
        print 'Failed to create the collection %s.' %(collection)

    # Collection handle
    collHandle = dbh[collection]

    # Create indexes
    collHandle.create_index([("geo",        GEO2D)],
                             name =         'tfl_geo_idx')
    
if __name__ == "__main__":
    main()