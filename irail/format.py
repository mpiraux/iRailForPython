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

import json

from .model import *


format_id = 'json'


def parse_stations(response):
    response_dict = json.loads(response)
    stations = [Station(**d) for d in response_dict['station']]
    return StationList(response_dict['timestamp'], response_dict['version'], stations)


def parse_schedules(response):
    response_dict = json.loads(response)

    def parse_connection_event(conn_event_dict, klass):  # TODO populate platform field using platforminfo
        conn_event_dict.pop('station')
        return klass(station=Station(**conn_event_dict.pop('stationinfo')),
                     direction=Station(conn_event_dict.pop('direction')['name'], *[None] * 4),  # Direction is not a real station
                     **conn_event_dict)

    connections = []
    for c_dict in response_dict['connection']:
        departure = parse_connection_event(c_dict.pop('departure'), Departure)
        arrival = parse_connection_event(c_dict.pop('arrival'), Arrival)
        connections.append(Connection(departure=departure, arrival=arrival, **c_dict))

    return ConnectionList(response_dict['timestamp'], response_dict['version'], connections)


def parse_liveboard(response):
    return as_obj(json.loads(response).pop('departures', {}).pop('departure', {}))


def parse_vehicle(response):
    return as_obj(json.loads(response).pop('vehicleinfo', {}))
