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

    def load_image(self, image_path, template_path="img/carat-template.jpg"):
        # Clean up data from earlier iterations if any
        self.reset()
        self.image = cv2.imread(image_path)
        self.template = cv2.imread(template_path)
        #show_spotify_large_details_border(self.image)
    
    def run(self, show_images=False):
        image = self.image
        template = self.template
        # Get basic dimensions of image
        template_h, template_w, _ = template.shape
        h, w, _ = image.shape

        is_large_spotify, top_left, bottom_right = is_image_large_spotify(image, template)

        #if is_large_spotify:
        #cv2.rectangle(image,top_left, bottom_right, 255, 2)
        #show_image_and_wait(image)
        #if show_images:
        #    cv2.rectangle(image,top_left, bottom_right, 255, 2)
            #show_image_and_wait(image)

        # Cut down image size if it's the large spotify image
        if is_large_spotify:
            image = get_spotify_large_details_image(image)
            #show_image_and_wait(image)

        # Binarize + Grayscale the image
        binarized = grayscale_and_binarize(image, 90, 255)

        #select_carat(image)
        # show_image_and_wait(binarized)

        # Save our gray image
        save_image_to_file('bw.png', binarized)

        # Run Tesseract OCR 
        text = get_ocr_text(binarized)

        # Algorithm - find word Spotify (for non-spotify-large images)
        # First non wordless line before that is artist
        # Line before that is song 

        # Split lines into array
        lines = text.splitlines()

        # Print out all lines
        for i, s in enumerate(lines):
            print "Line: " + str(i) +  ": " + s

        # Get the location of the detected word "Spotify" or just the line before the artist name
        if is_large_spotify:
            #show_spotify_large_details_border(image)
            # Try to find it with two colons (e.g. 0:03 ... 2:23)
            #show_image_and_wait(binarized)
            song_name = lines[0]
            artist = lines[1]
           # spotify_location = index_containing_two_colons(lines)
           # if spotify_location == -1:
                # Try to get just one location
           #     spotify_location = index_containing_substring_reversed_case_insensitive(lines, ":")
        else:
            spotify_location = index_containing_substring_case_insensitive(lines, "spotify")

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
                            # THIS DOES NOT WORK!
                            song_name = song_name[1:len(song_name)-2].strip()
                        break


        #print "Is large spotify? - " + str(is_large_spotify)
        #print "Image H = " + str(h) + " W = " + str(w)
        #print "SPOTIFY LINE LOCATION INDEX: " + str(spotify_location)


        #print "DETECTED ARTIST: " + str(artist)
        #print "DETECTED SONG NAME: " + str(song_name)
        self.artist = artist
        self.song_title = song_name

    def get_artist(self):
        return self.artist

    def get_song_title(self):
        return self.song_title



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

def index_containing_two_colons(the_list):
    for i, s in reversed(list(enumerate(the_list))):
        if s.count(':') == 2:
              return i
    return -1

def read_image(image_path):
    return cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

def show_image_and_wait(image, title="image"):
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(title, 600,600)
    cv2.imshow(title, image)

    k = cv2.waitKey(0)

def save_image_to_file(image_path, image):


    cv2.imwrite(image_path, image)

def get_spotify_large_details_image(image):
    h, w, _ = image.shape
    (x1, y1) = (int(0.12 * w), int(0.61 * h))
    (x2, y2) = (int(0.85 * w), int(0.725 * h))
    image = image[y1:y2, x1:x2] 
    #image = cv2.rectangle(image, topleft, botright,(255,0,0),2)
    #show_image_and_wait(image)
    return image

def select_carat(image):
    h, w, _ = image.shape
    (x1, y1) = (int(0.04 * w), int(0.06 * h))
    (x2, y2) = (int(0.11 * w), int(0.11 * h))
    #image = cv2.rectangle(image, topleft, botright,(255,255,0),2)
    image = cv2.Canny(image[y1:y2, x1:x2], 50, 200)
    cv2.imwrite("carat-template.jpg", image)
    show_image_and_wait(image)

def grayscale_and_binarize(image, lower_thresh, higher_thresh):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binarized = cv2.threshold(gray, lower_thresh, higher_thresh, cv2.THRESH_OTSU)[1]
    #show_image_and_wait(binarized)
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

# NOT ACCURATE ENOUGH!
def is_image_large_spotify(image, template, confidence_required=0.35):
    # Get basic dimensions of image
    template_h, template_w, _ = template.shape
    h, w, _ = image.shape

    (x1, y1) = (int(0.04 * w), int(0.06 * h))
    (x2, y2) = (int(0.11 * w), int(0.11 * h))
    #image = cv2.rectangle(image, topleft, botright,(255,255,0),2)
    image = image[y1:y2, x1:x2]
    # Apply template Matching and get confidence scores
    res = cv2.matchTemplate(image,template,cv2.TM_CCOEFF_NORMED)
    #show_image_and_wait(image)
    #show_image_and_wait(template)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    print "Confidence val for image type detection (min_val): " + str(min_val) 
    print "Confidence val for image type detection (max_val): " + str(max_val) 
    top_left = max_loc
    bottom_right = (top_left[0] + template_w, top_left[1] + template_h)

    # Return based on whether we are confident that we spotted the carat correctly
    return (True, top_left, bottom_right) if max_val > confidence_required else (False, top_left, bottom_right)


# ------ END UTILITY METHODS ------

if __name__ == "__main__":
    #for i in range(1, 83):
    i = 46
    recog = SpotifyImageRecognizer()
    recog.load_image("img/tests/" + str(i) + ".jpg")
    recog.run()
    print "Artist: " + str(recog.get_artist())
    print "Song Title: " + str(recog.get_song_title())
    '''
    recog = SpotifyImageRecognizer()
    recog.load_image("img/lockscreen.jpg")
    recog.run()
    print "Artist: " + recog.get_artist()
    print "Song Title: " + recog.get_song_title()

    recog.reset()
    recog.load_image("img/spotify-large.jpg")
    recog.run()
    print "Artist: " + recog.get_artist()
    print "Song Title: " + recog.get_song_title()

    recog.reset()
    recog.load_image("img/notif-clock.jpg")
    recog.run()
    print "Artist: " + recog.get_artist()
    print "Song Title: " + recog.get_song_title()


    recog.reset()
    recog.load_image("img/notif-noclock.jpg")
    recog.run()
    print "Artist: " + recog.get_artist()
    print "Song Title: " + recog.get_song_title()
    '''
    
 



