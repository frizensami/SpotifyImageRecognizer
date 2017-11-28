# import the necessary packages
from PIL import Image
import pytesseract
import argparse
import cv2
import os
import string
import csv


'''
Promised interface for SpotifyImageRecognizer:

recog = SpotifyImageRecognizer()

recog.load_image("<path to image>") <--- might throw errors!

recog.run() <-- might throw errors!

# both of the calls below may return None if couldn't get an artist or song name
artist = recog.get_artist()
title = recog.get_title()
'''
class SpotifyImageRecognizer():
    '''
    A class for recognizing images from a screenshot of 
    1. A spotify notification on an Android phone
    2. The spotify main application screen
    '''
    def reset(self):
        self.image = None
        self.template = None
        self.artist = None
        self.song_title = None

    def load_image(self, image_path, template_path="img/upside-down-carat.png"):
        # Clean up data from earlier iterations if any
        self.reset()
        self.image = cv2.imread(image_path)
        self.template = cv2.imread(template_path)
    
    def run(self):
        image = self.image
        template = self.template
        # Get basic dimensions of image
        template_h, template_w, _ = template.shape
        h, w, _ = image.shape

        is_large_spotify, top_left, bottom_right = is_image_large_spotify(image, template)
        cv2.rectangle(image,top_left, bottom_right, 255, 2)
        show_image_and_wait(image)

        # Binarize + Grayscale the image
        binarized = grayscale_and_binarize(image, 90, 255)
        show_image_and_wait(binarized)

        # Save our gray image
        save_image_to_file('bw.png', binarized)

        # Run Tesseract OCR 
        text = get_ocr_text(binarized)

        # Get the set of bounding boxes for all our text
        #boxes = get_ocr_bounding_boxes('bw.png')

        # Overlay it onto our black and white image
        #img = overlay_ocr_bounding_boxes('bw.png', boxes)
        #show_image_and_wait(img)

        # Algorithm - find word Spotify (for non-spotify-large images)
        # First non wordless line before that is artist
        # Line before that is song 

        # Split lines into array
        lines = text.splitlines()

        # Print out all lines
        for i, s in enumerate(lines):
            print "Line: " + str(i) +  ": " + s

        # Get the location of the detected word "Spotify"
        if is_large_spotify:
            spotify_location = index_containing_substring_reversed_case_insensitive(lines, ":")
        else:
            spotify_location = index_containing_substring_case_insensitive(lines, "spotify")

        # IF THIS IS THE TYPE OF IMAGE WE ARE GETTING (aka notification with spotify)
        # Get a more specific bounding box (from spotify to right of screen)
        #boxes_alnum = filter(lambda y: y[0].isalnum(), boxes)
        #allwords = map(lambda x: x[0], boxes_alnum)
        #joinedwords = str("".join(allwords))


        # Find location of substring spotify
        #idx = joinedwords.lower().find("spotify") 
        #c = boxes_alnum[idx]
        #(x1, y1) = (int(c[1]),h-int(c[2])) # Bottom left corner
        #(x2, y2) = (int(c[3]),h-int(c[4])) # Top right corner
        # This is the location of the Spotify word
        #roi = img[(y2-5):(y1+5), (x1-5):(x2+5)] 
        #roi = img[:y1+10, x1-10:]
        #cv2.imshow("ROI", roi)
        #cv2.waitKey(0)

        print "Is large spotify? - " + str(is_large_spotify)
        #print "Boxes_alnum: " + str(boxes_alnum)
        #print "All joined words: " + str(joinedwords)
        #print "Spotify detected index: " + str(idx)
        #print "Boxes from idx: " + str(boxes_alnum[idx:])
        print "Image H = " + str(h) + " W = " + str(w)
        #print "Rectangle coordinates: " + str((int(c[1]),h-int(c[2]),int(c[3]),h-int(c[4])))
        #print "(x1, y1): " + str((x1, y1))
        #print "(x2, y2): " + str((x2, y2))


        print "SPOTIFY LINE LOCATION INDEX: " + str(spotify_location)

        # Define alphanumberic set
        alnum = set(string.letters + string.digits)
        # From the spotify location upwards
        artist = None
        song_name = None
        for i in range(spotify_location-1, -1, -1):
            line = lines[i]

            # Alphanumeric line detected
            if len(set(line) & alnum) > 0:
                # Remove K I I N which is what the pause and left/right arrows are detected as
                if artist is None:
                    artist = line.encode('ascii', 'ignore').replace('K I I N','').strip()
                elif song_name is None:
                    song_name = line.encode('ascii', 'ignore').replace('K I I N','').strip()

                    # If it's the large spotify version, remove the +/tick and the semicolon
                    if is_large_spotify:
                        song_name = song_name[1:len(song_name)-1].strip()
                    break
            


        print "DETECTED ARTIST: " + str(artist)
        print "DETECTED SONG NAME: " + str(song_name)



# ----- UTILITY METHODS -----

def index_containing_substring_case_insensitive(the_list, substring):
    for i, s in enumerate(the_list):
        if substring.lower() in s.lower():
              return i
    return -1

def index_containing_substring_reversed_case_insensitive(the_list, substring):
    for i, s in reversed(list(enumerate(the_list))):
        if substring.lower() in s.lower():
              return i
    return -1

def read_image(image_path):
    return cv2.imread(image_path)

def show_image_and_wait(image, title="image"):
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(title, 600,600)
    cv2.imshow(title, image)

    k = cv2.waitKey(0)

def save_image_to_file(image_path, image):
    cv2.imwrite(image_path, image)

def grayscale_and_binarize(image, lower_thresh, higher_thresh):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binarized = cv2.threshold(gray, lower_thresh, higher_thresh, cv2.THRESH_BINARY)[1]
    return binarized

def get_ocr_text(image):
    # Run Tesseract OCR 
    textImage = Image.fromarray(image)
    text = pytesseract.image_to_string(textImage)
    return text

def get_ocr_bounding_boxes(file_name):
    pytesseract.pytesseract.run_tesseract(file_name, 'output', lang=None, boxes=True, config="hocr")

    # To read the coordinates
    boxes = []
    with open('output.box', 'rb') as f:
        reader = csv.reader(f, quotechar='"', quoting=csv.QUOTE_NONE, delimiter = ' ')
        for row in reader:
            if(len(row)==6):
                boxes.append(row)
    
    return boxes

def overlay_ocr_bounding_boxes(file_name, boxes):
    img = cv2.imread(file_name)
    for b in boxes:
        img = cv2.rectangle(img,(int(b[1]),h-int(b[2])),(int(b[3]),h-int(b[4])),(255,0,0),2)
    return img

def is_image_large_spotify(image, template, confidence_required=0.8):
    # Get basic dimensions of image
    template_h, template_w, _ = template.shape
    h, w, _ = image.shape

    # Apply template Matching and get confidence scores
    res = cv2.matchTemplate(image,template,cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    print "CONFIDENCE VAL: " + str(max_val) 
    top_left = max_loc
    bottom_right = (top_left[0] + template_w, top_left[1] + template_h)

    # Return based on whether we are confident that we spotted the carat correctly
    return (True, top_left, bottom_right) if max_val > confidence_required else (False, top_left, bottom_right)


# ------ END UTILITY METHODS ------
    
recog = SpotifyImageRecognizer()
recog.load_image("img/lockscreen.jpg")
recog.run()


# Set of example images
#image = read_image("img/lockscreen.jpg")
# load the example image and convert it to grayscale
#image = cv2.imread("img/spotify-large.jpg")
#image = cv2.imread("img/notif-clock.jpg")
#image = cv2.imread("img/notif-noclock.jpg")

# Get pause / play template to match
#template = cv2.imread('img/upside-down-carat.png')





