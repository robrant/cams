import os
import sys
import Image
import ImageDraw

def createThumbnail(inFilePath, thumbsOutDir, size=50):
    ''' Creates a thumbnail per image and saves it out'''
    
    # Get the file name for the thumbnail
    thumb = os.path.splitext(inFilePath) + "_thumb.jpg"  
    
    # Set the size of the thumbnail
    thumbSize = size, size 
    
    im = Image.open(inFilePath, thumbsOutDir)
    im.thumbnail(thumbSize)
    im.save(thumb, "JPEG")

    