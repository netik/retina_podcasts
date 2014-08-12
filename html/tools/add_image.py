#!/usr/bin/python
import sys

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error

if len(sys.argv) != 3:
    print >>sys.stderr, "Usage: %s mp3file jpegfile" % sys.argv[0]
    sys.exit(1)

audio = MP3(sys.argv[1], ID3=ID3)


# add ID3 tag if it doesn't exist
try:
    audio.add_tags()
except error:
    pass

audio.tags.add(
    APIC(
        encoding=3, # 3 is for utf-8
        mime='image/jpeg', # image/jpeg or image/png
        type=3, # 3 is for the cover image
        desc=u'Cover',
        data=open(sys.argv[2]).read()
    )
)
audio.save()
