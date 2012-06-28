Current Setup: @ 28 Jul 2012

/eclipseWorkspace/cams - is the working area for this code. It is also the code being committed out to GIT.

/dotcloudDev/cams-on-dotcloud/ - is the area from which the project is
being pushed to dotcloud. It also contains a postinstall file which
handles the extra build of a /logs directory and the building of the 
cron job that calls data from the tfl website.

Edits should be made to the code in /eclipseWorkspace, which should be 
transferred to /dotcloudDev directory and then pushed from there.

To access mongo on the server: dotcloud run cams.data mongo
To push the project: dotcloud push cams
To ssh into the server: dotcloud ssh cams.worker

