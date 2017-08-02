# -*- coding: utf-8 -*-

# Copyright (c) 2011, Wouter Horré
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import urllib.request, urllib.error, urllib.parse
from .model import *
from .format import *
from .exception import *

#curl 'api.irail.be/liveboard/?station=gentbruggee&format=json'

BASE_URL="http://api.irail.be/"
URLS={
    'stations':'stations',
    'schedules':'connections',
    'liveboard': 'liveboard',
    'vehicle': 'vehicle'
}
DEFAULT_ARGS="?format=json"

class iRailAPI:

  def __init__(self, format=None, lang=None):
    self.set_format(format)
    self.set_lang(lang)

  def format(self):
    return self.__format

  def set_format(self, format):
    if format:
      self.__format = format
    else:
      self.__format = JsonFormat()

  def lang(self):
    return self.__lang

  def set_lang(self, lang):
    if lang:
      self.__lang = lang
    else:
      self.__lang = "EN"
  
  def do_request(self, method, args=None):
    url = BASE_URL + method + "/"
    url += "?format=" + str(self.format())
    url += "&lang=" + self.lang()
    if args:
      for key in list(args.keys()):
        url += "&" + key + "=" + args[key]
    try:
      return urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
      if e.code >= 400 and e.code < 500:
        raise ClientError(e)
      elif e.code >= 500 and e.code < 500:
        raise ServerError(e)
  
  def get_stations(self):
    """Retrieve the list of stations"""
    response = self.do_request(URLS['stations'])
    return self.__format.parse_stations(response)

  def search_stations(self, start):
    """Retrieve the list of stations that start with a given string"""
    stations = self.get_stations()
    return [station for station in stations.stations() if station.name().lower().startswith(start.lower())]

  def get_schedules_by_names(self, fromStation, toStation, date=None, time=None, timeSel=None, types=None):
    """Get the connections between to stations given by name"""
    args = {}
    args['from'] = fromStation
    args['to'] = toStation
    response = self.do_request(URLS['schedules'], args)
    return self.__format.parse_schedules(response)

  def get_schedules(self, fromStation, toStation, date=None, time=None, timeSel=None, typesOfTransport=None):
    return self.get_schedule_by_names(fromStation.name(), toStation.name(), date, time, timeSel, typesOfTransport)

  def get_liveboard_by_name(self, name, date=None, time=None, arrdep='DEP'):
    args = {'station': name}
    response = self.do_request(URLS['liveboard'], args)
    return self.__format.parse_liveboard(response)

  def get_liveboard_by_id(self, id, date=None, time=None, arrdep='DEP'):
    args = {'id': id}
    response = self.do_request(URLS['liveboard'], args)
    return self.__format.parse_liveboard(response)

  def get_vehicle_by_id(self, id):
    args = {'id': id}
    response = self.do_request(URLS['vehicle'], args)
    return self.__format.parse_vehicle(response)

