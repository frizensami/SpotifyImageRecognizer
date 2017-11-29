# Simple test script runner
from recognizer import SpotifyImageRecognizer

# Utility methods
def group(lst, n):
    """group([0,3,4,10,2,3], 2) => [(0,3), (4,10), (2,3)]
    
    Group a list into consecutive n-tuples. Incomplete tuples are
    discarded e.g.
    
    >>> group(range(10), 3)
    [(0, 1, 2), (3, 4, 5), (6, 7, 8)]

    http://code.activestate.com/recipes/303060-group-a-list-into-sequential-n-tuples/
    """
    return zip(*[lst[i::n] for i in range(n)]) 

if __name__ == "__main__":
    # Read entire test file
    f = open("img/tests/test.txt","r") 
    file_lines = f.read().splitlines()
    f.close()

    # Group the file lines by the file structure: image name <br> song name <br> artist <br>
    test_cases = group(file_lines, 4)

    total_cases = len(test_cases)
    failures = 0

    for path, title, artist, _ in test_cases:
        path = "img/tests/" + path
        print "\n---------Running test for: " + str((path, title, artist)) + "---------------"
        recog = SpotifyImageRecognizer()
        recog.load_image(path)
        recog.run()

        test_match = True
        if recog.get_artist() != artist:
            print "TEST CASE FAILURE FOR " + path + ".\nExpected ARTIST: " + artist + " - GOT ARTIST: " + str(recog.get_artist())
            test_match = False

        if recog.get_song_title() != title:
            print "TEST CASE FAILURE FOR " + path + "\nExpected SONG TITLE: " + title + " - GOT SONG TITLE: " + str(recog.get_song_title())
            test_match = False

        if test_match:
            print "Test success for: " + str((path, title, artist))
        else:
            failures += 1
        
        print "-------------------------------------------------------------"
    
    print "Total Failures: " + str(failures) + "/" + str(total_cases)
    
        






