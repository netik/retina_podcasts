#!/usr/bin/python
#
# renderpage.py
# Build the podcasting home page, including:
#
#   * State of icecast server (if we're live) 
#   * All available podcasts rendered from
#     showindex_multi.json and mustache templates.
#
# J. Adams < jna@retina.net >
# 8/5/2014
#
# TODO: Don't touch the destination file if our state hasn't changed.
#       Better error handling - right now we have none. 

import json
import pystache
from pytz import timezone
import requests
import rfc822
import time

class Index(object):
  """ methods for the index.mustache page """
  def is_live(self):
      """ right now we only broadcast under /wg, see if it is up """
      r = requests.get('http://podcast.retina.net:8000/')
      if r.status_code == 200:
          if r.text.find("Mount Point /wg") > -1:
              return True
      else:
          return False

  def shows(self):
    fp = open("showindex_multi.json","r")
    shows = json.load(fp)
    return shows['shows']

class Rss(object):
  """ methods for rendering the rss index """
  def shows(self):
    fp = open("showindex_multi.json","r")
    shows = json.load(fp)

    # this RSS feed is only the first show (wg) episode list. 
    return shows['shows'][0]['show']['episodes']

# set up the renderer
renderer = pystache.Renderer(search_dirs="/retina/podcast/html/templates")

# render the index page 
page = Index()
parsed = renderer.render(page)
fout = open("index.html","w")
print >>fout, parsed
fout.close()

# render the RSS feed 
page = Rss()
parsed = renderer.render(page)
fout = open("wg/wicked_grounds.rss","w")
print >>fout, parsed
fout.close()
