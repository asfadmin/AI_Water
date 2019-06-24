import urllib, sys, getopt, os
def main(argv):
   DESTINATION_FOLDER = argv[0]
   if (DESTINATION_FOLDER[-1:]!="/"):
      DESTINATION_FOLDER = DESTINATION_FOLDER + "/"
   if not os.path.exists(DESTINATION_FOLDER):
      print "Creating folder " + DESTINATION_FOLDER
      os.makedirs(DESTINATION_FOLDER)
   DATASET_NAME = argv[1]
   longs = [str(w) + "W" for w in range(180,0,-10)]
   longs.extend([str(e) + "E" for e in range(0,180,10)])
   lats = [str(s) + "S" for s in range(50,0,-10)]
   lats.extend([str(n) + "N" for n in range(0,90,10)])
   fileCount = len(longs)*len(lats)
   counter = 1
   for lng in longs:
      for lat in lats:
        filename = DATASET_NAME+ "_" + str(lng) + "_" + str(lat) + ".tif"
        if os.path.exists(DESTINATION_FOLDER + filename):
           print DESTINATION_FOLDER + filename + " already exists - skipping"
        else:
           url = "http://storage.googleapis.com/global-surface-water/downloads2/" + DATASET_NAME + "/" + filename
           code = urllib.urlopen(url).getcode()
           if (code != 404):
              print "Downloading " + url + " (" + str(counter) + "/" + str(fileCount) + ")"
              urllib.urlretrieve(url, DESTINATION_FOLDER + filename)
           else:
              print url + " not found"
        counter += 1
if __name__ == "__main__":
   main(sys.argv[1:])