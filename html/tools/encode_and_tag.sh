#!/bin/bash
#
# encode_and_tag.sh
#
# Given an AIF file, encode the file to MP3 with LAME. 
# Then, Apply appropriate tag and cover art for Wicked Grounds
#
# we encode to 96khz, stereo

BITRATE=96  
ART=WGLogo.jpg

if [ "$1" == "" ]; then
  echo "Usage: $0 aifaudiofile"
  exit
fi

# encode the file
lame -b 96 $1 

if [ $? != 0 ]; then
  echo "Encoding failed. Bye."
  exit
fi

filename=$1
mp3filename=${filename/.aif/.mp3}

# this sucks, move everything to one script. 
# tag it
./apply_basic_tags.py $mp3filename

# add image 
./add_image.py $mp3filename ${ART}

echo "Done! Now go update the RSS file."

