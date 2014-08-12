#!/usr/bin/python
import sys
from ID3 import *
from datetime import date

try:
    id3info = ID3(sys.argv[1])
    print id3info

    epnum = raw_input("Episode number? ")  
    comment = raw_input("Comment? ")  

    id3info['TITLE'] = "Cafe Podcast: Episode %s" % epnum
    id3info['ARTIST'] = "Wicked Grounds"
    id3info['ALBUM'] = "Cafe Audio Podcast"
    id3info['YEAR'] = "%d" % date.today().year
    id3info['GENRE'] = "Other"
    id3info['COMMENT'] = comment

    for k, v in id3info.items():
        print k, ":", v
except InvalidTagError, message:
    print "Invalid ID3 tag:", message
