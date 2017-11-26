# import the necessary packages
from PIL import Image
import pytesseract
import argparse
import cv2
import os
import string



def index_containing_substring(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
              return i
    return -1

def index_containing_substring_reversed(the_list, substring):
    for i, s in reversed(list(enumerate(the_list))):
        if substring in s:
              return i
    return -1

# load the example image and convert it to grayscale
#image = cv2.imread("img/lockscreen.jpg")
image = cv2.imread("img/spotify-large.jpg")
#image = cv2.imread("img/notif-clock.jpg")
#image = cv2.imread("img/notif-clock.jpg")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.threshold(gray, 90, 255, cv2.THRESH_BINARY)[1]
cv2.imshow('image', gray)
k = cv2.waitKey(0)
cv2.destroyAllWindows()
gray = Image.fromarray(gray)
text = pytesseract.image_to_string(gray)

# Algorithm - find word Spotify (for non-spotify-large images)
# First non wordless line before that is artist
# Line before that is song 

# Split lines into array
lines = text.splitlines()

# Print out all lines
for i, s in enumerate(lines):
    print "Line: " + str(i) +  ": " + s
spotify_location = index_containing_substring(lines, "Spotify")
if spotify_location == -1:
    # try again by searchig for a colon
    spotify_location = index_containing_substring_reversed(lines, ":")

print "SPOTIFY LINE LOCATION INDEX: " + str(spotify_location)

# Define alphanumberic set
alnum = set(string.letters + string.digits)
# From the spotify location downwards
artist = None
song_name = None
for i in range(spotify_location-1, -1, -1):
    line = lines[i]

    # Alphanumeric line detected
    if len(set(line) & alnum) > 0:
        if artist is None:
            artist = line
        elif song_name is None:
            song_name = line
            break


print "DETECTED ARTIST: " + artist
print "DETECTED SONG NAME: " + song_name



#WORD 'SPOTIFY'" + str(index_containing_substring(lines, "Spotify"))
