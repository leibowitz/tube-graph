from __future__ import print_function
import collections
import json
from py2neo import Graph

def encode_name(s):
    return ''.join(e for e in s if e.isalnum())

class Tube(object):
    def __init__(self):
        self._links = collections.defaultdict(collections.defaultdict)
        self._changes = collections.defaultdict(collections.defaultdict)

    def add_link(self, origin, destination, name, data):
        if origin in self._links and destination in self._links[origin]:
            self._links[origin][destination][name] = data
            return
        if destination in self._links and origin in self._links[destination]:
            self._links[destination][origin][name] = data
            return

        self._links[origin][destination] = {name: data}

    def add_change(self, station, data=None, line=None):
        if station not in self._changes:
            self._changes[station] = {'lines': set()}
        if line:
            self._changes[station]['lines'].add(line)
        if data:
            self._changes[station].update(data)

    def stations(self):
        return self._changes

    def interchanges(self):
        for station, data in self.stations().items():
            lines = data['lines']
            while len(lines) > 1:
                lineto = lines.pop()
                for linefrom in lines:
                    yield station, linefrom, lineto

    def links(self):
        for origin, destinationdata in self._links.items():
            for destination, station_data in destinationdata.items():
                for line, data in station_data.items():
                    yield origin, destination, line, data

tube = Tube()
stations = collections.defaultdict(set)

commands = []

with open('./tube-data2.json') as data_file:
    data = json.load(data_file)
    for x in data['stations']:
        tube.add_change(x['name'], x)
    for x in data['links']:
        tube.add_link(x['from'], x['to'], x['linkType'], x)
        tube.add_change(x['from'], line=x['linkType'])
        tube.add_change(x['to'], line=x['linkType'])

stations = collections.OrderedDict(sorted(tube.stations().items()))
for station, data in stations.items():
    encoded_station = encode_name(station)
    # station
    commands.append("CREATE (%s:Station {name:%s, latitude: %f, longitude: %f})" % (encoded_station, json.dumps(station), data['lat'], data['lng']))
    for line in data['lines']:
        stop_name = encoded_station + "_" + encode_name(line)
        # stop on a line
        commands.append("CREATE (%s:Stop {line: %s, station: %s})" % (stop_name, json.dumps(line), json.dumps(station)))
        # Getting on
        commands.append("MATCH (a:Station), (b:Stop) WHERE a.name = %s AND b.line = %s AND b.station = %s CREATE (a)-[:ROUTE {time: %d}]->(b)" % (json.dumps(station), json.dumps(line), json.dumps(station), 150))
        # Getting off
        commands.append("MATCH (a:Stop), (b:Station) WHERE a.line = %s AND a.station = %s AND b.name = %s CREATE (a)-[:ROUTE {time: %d}]->(b)" % (json.dumps(line), json.dumps(station), json.dumps(station), 150))

for (origin, to, line, data) in tube.links():
    stop_name1 = encode_name(origin) + "_" + encode_name(line)
    stop_name2 = encode_name(to) + "_" + encode_name(line)
    commands.append("MATCH (a:Stop), (b:Stop) WHERE a.line = %s AND a.station = %s AND b.line = %s AND b.station = %s CREATE (a)-[:ROUTE {time: %d}]->(b)" % (json.dumps(line), json.dumps(origin), json.dumps(line), json.dumps(to), data['durationSeconds']))

graph = Graph("http://neo4j:passwd@localhost:7474/db/data/")

for q in commands:
    graph.run(q)


