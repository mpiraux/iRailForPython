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


# The iRail api returns all ints and timestamps as strings
# so the python api makes the same mistake not my fault!
import collections
from datetime import datetime, timedelta

GeographicCoordinate = collections.namedtuple('GeographicCoordinate', ['longitude', 'latitude'])


def as_obj(c):
    class AttrDict(dict):
        def __init__(self, *args, **kwargs):
            super(AttrDict, self).__init__(*args, **kwargs)
            self.__dict__ = self

    if isinstance(c, collections.Sequence):
        return type(c)(as_obj(e) for e in c)
    elif type(c) is dict:
        a_d = AttrDict()
        a_d.update(c)
        return a_d
    raise NotImplementedError


class ResultList:
    def __init__(self, timestamp, version):
        self.timestamp = int(timestamp)
        self.date = datetime.fromtimestamp(self.timestamp)
        self.version = tuple(int(s) for s in version.split('.'))


class StationList(ResultList):
    def __init__(self, timestamp, version, stations, **kwargs):
        self.stations = stations
        ResultList.__init__(self, timestamp, version)

    def __iter__(self):
        return iter(self.stations)

    def __str__(self):
        return '[' + ', '.join(str(station) for station in self.stations) + ']'

    def __repr__(self):
        return '{}(timestamp={}, version={}, stations={})'.format(self.__class__.__name__,
            *(repr(e) for e in (self.timestamp, self.version, self.stations))
        )


class Station:
    def __init__(self, name, standardname, id, locationX, locationY, **kwargs):
        self.name = name
        self.standardname = standardname
        self.id = id
        self.locationX = float(locationX or 0)
        self.locationY = float(locationY or 0)
        self.location = GeographicCoordinate(locationX, locationY)

    def __str__(self):
        return "Station {} | {} @ ({}, {})".format(self.id, self.name, self.locationY, self.locationX)

    def __repr__(self):
        return '{}(name={}, standardname={}, id={}, locationX={}, locationY={})'.format(self.__class__.__name__,
            *(repr(e) for e in (self.name, self.standardname, self.id, self.locationX, self.locationY))
        )


class ConnectionList(ResultList):
    def __init__(self, timestamp, version, connections, **kwargs):
        self.connections = connections
        ResultList.__init__(self, timestamp, version)

    def __iter__(self):
        return iter(self.connections)

    def __repr__(self):
        return '{}(timestamp={}, version={}, connections={})'.format(self.__class__.__name__,
            *(repr(e) for e in (self.timestamp, self.version, self.connections))
        )


class Connection:
    def __init__(self, id, departure, arrival, duration, vias=None, **kwargs):
        self.id = int(id)
        self.departure = departure
        self.vias = vias
        self.arrival = arrival
        self.duration = int(duration)
        self.duration_timedelta = timedelta(seconds=self.duration)

    def __str__(self):
        s = """Connection ({}):
  departure: {}
  arrival: {}
  vias: {}
  duration: {}"""
        return s.format(self.id, self.departure, self.arrival, self.vias, self.duration)

    def __repr__(self):
        return '{}(id={}, departure={}, arrival={}, vias={}, duration={})'.format(self.__class__.__name__,
            *(repr(e) for e in (self.id, self.departure, self.arrival, self.vias, self.duration))
        )


class ConnectionEvent:
    def __init__(self, station, platform, time, delay, vehicle, direction, **kwargs):
        self.station = station
        self.platform = platform
        self.time = int(time)
        self.date = datetime.fromtimestamp(self.time)
        self.delay = int(delay)
        self.delay_timedelta = timedelta(seconds=self.delay)
        self.vehicle = vehicle
        self.direction = direction

    def __str__(self):
        return "@{} (+{}) -> {}".format(self.time, self.delay, self.station)

    def __repr__(self):
        return '{}(station={}, platform={}, time={}, delay={}, vehicle={}, direction={})'.format(self.__class__.__name__,
             *(repr(e) for e in (self.station, self.platform, self.time, self.delay, self.vehicle, self.direction))
        )


class Arrival(ConnectionEvent):
    pass


class Departure(ConnectionEvent):
    pass
