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

from pytz import timezone
from datetime import tzinfo, timedelta, datetime
import json
import pystache
import requests
import rfc822
import time

# In the US, DST starts at 2am (standard time) on the first Sunday in April.
# and ends at 2am (DST time; 1am standard time) on the last Sunday of Oct.
# which is the first Sunday on or after Oct 25.
DSTSTART = datetime(1, 4, 1, 2)
DSTEND = datetime(1, 10, 25, 1)
ZERO = timedelta(0)
HOUR = timedelta(hours=1)

def first_sunday_on_or_after(dt):
  days_to_go = 6 - dt.weekday()
  if days_to_go:
    dt += timedelta(days_to_go)
  return dt

class UTC(tzinfo):
  """UTC"""
  def utcoffset(self, dt):
    return ZERO
  def tzname(self, dt):
    return "UTC"
  def dst(self, dt):
    return ZERO

class USTimeZone(tzinfo):
  def __init__(self, hours, reprname, stdname, dstname):
    self.stdoffset = timedelta(hours=hours)
    self.reprname = reprname
    self.stdname = stdname
    self.dstname = dstname

  def __repr__(self):
    return self.reprname

  def tzname(self, dt):
    if self.dst(dt):
      return self.dstname
    else:
      return self.stdname

  def utcoffset(self, dt):
    return self.stdoffset + self.dst(dt)

  def dst(self, dt):
    if dt is None or dt.tzinfo is None:
      # An exception may be sensible here, in one or both cases.
      # It depends on how you want to treat them.  The default
      # fromutc() implementation (called by the default astimezone()
      # implementation) passes a datetime with dt.tzinfo is self.
      return ZERO
    assert dt.tzinfo is self

    # Find first Sunday in April & the last in October.
    start = first_sunday_on_or_after(DSTSTART.replace(year=dt.year))
    end = first_sunday_on_or_after(DSTEND.replace(year=dt.year))

    # Can't compare naive to aware objects, so strip the timezone from
    # dt first.
    if start <= dt.replace(tzinfo=None) < end:
      return HOUR
    else:
      return ZERO

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
    fp = open("showindex.json","r")
    shows = json.load(fp)

    # Convert the GMT times into something more friendly for HTML reading
    # incoming times are always in RSS format, we want them in US/Pacific 
    # (Also, what the fuck year is this. Why am I writing this code.)
    utc = UTC()
    Pacific = USTimeZone(-8, "Pacific",  "PST", "PDT")
    for show in shows['shows']:
      n = 0
      for e in show['show']['episodes']:
        parsed_date = e['date']
        d = datetime.strptime( e['date'], "%a, %d %b %Y %H:%M:%S GMT" )
        aware = d.replace(tzinfo=utc)
        show['show']['episodes'][n]['date'] = aware.astimezone(Pacific).strftime("%A, %B %e, %Y")
        n = n + 1

    return shows['shows']

class Rss(object):
  """ methods for rendering the rss index """
  def shows(self):
    fp = open("showindex.json","r")
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
