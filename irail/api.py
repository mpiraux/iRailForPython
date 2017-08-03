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

import urllib.error
import urllib.parse
from urllib.parse import quote
import urllib.request

import irail.format
from .exception import *

BASE_URL = "http://api.irail.be/"
URLS = {
    'stations': 'stations',
    'schedules': 'connections',
    'liveboard': 'liveboard',
    'vehicle': 'vehicle'
}
DEFAULT_ARGS = "?format=json"


class iRailAPI:
    def __init__(self, formatter=irail.format, lang='EN'):
        self.formatter = formatter
        self.lang = lang

    def do_request(self, method, **kwargs):
        url = '{}{}/?format={}&lang={}'.format(BASE_URL, method, self.formatter.format_id, self.lang)
        for key, value in kwargs.items():
            url += ('&{}={}'.format(quote(key), quote(value)))
        try:
            return urllib.request.urlopen(url).read().decode('utf-8')
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500:
                raise ClientError(e)
            elif e.code >= 500:
                raise ServerError(e)

    def get_stations(self):
        """Retrieve the list of stations"""
        response = self.do_request(URLS['stations'])
        return self.formatter.parse_stations(response)

    def search_stations(self, start):
        """Retrieve the list of stations that start with a given string"""
        stations_list = self.get_stations()
        stations_list.stations = [station for station in stations_list if station.name.lower().startswith(start.lower())]
        return stations_list

    def get_schedules_by_names(self, from_station, to_station, date=None, time=None, time_sel=None, types=None):
        """Get the connections between to stations given by name"""
        args = {'from': from_station, 'to': to_station}
        response = self.do_request(URLS['schedules'], **args)
        return self.formatter.parse_schedules(response)

    def get_schedules(self, from_station, to_station, date=None, time=None, time_sel=None, transport_types=None):
        return self.get_schedules_by_names(from_station.name, to_station.name, date, time, time_sel, transport_types)

    def get_liveboard_by_name(self, name, date=None, time=None, arrdep='DEP'):
        response = self.do_request(URLS['liveboard'], station=name)
        return self.formatter.parse_liveboard(response)

    def get_liveboard_by_id(self, station_id, date=None, time=None, arrdep='DEP'):
        response = self.do_request(URLS['liveboard'], id=station_id)
        return self.formatter.parse_liveboard(response)

    def get_vehicle_by_id(self, vehicle_id):
        response = self.do_request(URLS['vehicle'], id=vehicle_id)
        return self.formatter.parse_vehicle(response)
