from __future__ import print_function
import collections
import json
from py2neo import Graph

class Tube(object):
    def __init__(self):
        self._links = collections.defaultdict(collections.defaultdict)
        self._changes = collections.defaultdict(collections.defaultdict)

    def add_link(self, origin, destination, name, data):
        #if 'lines' in data:
        #    data['lines'] = set(data['lines'])
        #else:
        #    data['lines'] = set()

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
        #for station, lines in self._changes.items():
        #    yield station, lines

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
                    #print(data)
                    #originkeys = set(list(self._links[origin].keys()))
                    #destinationkeys = set(list(self._links[destination].keys()))
                    #if origin in self._links:
                        #if destination in self._links and len(destinationkeys):
                        #    data['lines'] = originkeys.union(destinationkeys)
                        #else:
                        #    data['lines'] = originkeys
                    #elif destination in self._links:
                    #    data['lines'] = destinationkeys
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
        #print(x['from'], "=>", x['to'], "(", x['linkType'], x['durationSeconds'], ")")

#print("//"+"="*40)
#print("//Tube Stations")
#print("//"+"="*40)
stations = collections.OrderedDict(sorted(tube.stations().items()))
for station, data in stations.items():
    #print(station, lines)
    encoded_station = ''.join(e for e in station if e.isalnum())
    #commands.append("CREATE (%s:Station {name:%s, lines: %s})" % (encoded_station, json.dumps(station), list(data['lines'])))
    for line in data['lines']:
        commands.append("CREATE (%s:Station {name:%s, line: %s, latitude: %f, longitude: %f})" % (encoded_station, json.dumps(station), json.dumps(line), data['lat'], data['lng']))

#print("//"+"="*40)
#print("//Stops")
#print("//"+"="*40)

for (origin, to, line, data) in tube.links():
    #print(line, ":", origin, "=>", to, "(", data['durationSeconds'], "s)")
    from_station = ''.join(e for e in origin if e.isalnum())
    to_station = ''.join(e for e in to if e.isalnum())
    command = "MATCH (a:Station),(b:Station) " + ("WHERE a.name = %s AND a.line = %s AND b.name = %s AND b.line = %s " % (json.dumps(origin), json.dumps(line), json.dumps(to), json.dumps(line))) + "CREATE (a)-[:CONNECT {line:%s, time: %d}]->(b)" % (json.dumps(line), data['durationSeconds'])
    #print("CREATE (%s)-[:CONNECT {lines:%s}]->(%s)" % (from_station, [line], to_station))
    commands.append(command)

#print("//"+"="*40)
#print("//Stops with changes")
#print("//"+"="*40)
for (station, origin, to) in tube.interchanges():
    encoded_station = ''.join(e for e in station if e.isalnum())
    #print(station, ":", origin, "X>", to, "(", 5*60 ,"s)")
    command = "MATCH (a:Station),(b:Station) " + ("WHERE a.name = %s AND a.line = %s AND b.name = %s AND b.line = %s " % (json.dumps(station), json.dumps(origin), json.dumps(station), json.dumps(to))) + "CREATE (a)-[:CONNECT {time: 300}]->(b)"
    commands.append(command)

    #print("CREATE (OxfordCircus)-[:CONNECT {lines:['central']}]->(BondStreet)")

#CREATE (BondStreet:Station {name:'Bond Street', latitude: 12, longitude: 11, lines: ['central', 'jubilee']})

graph = Graph("http://neo4j:passwd@localhost:7474/db/data/")

#tx = session.create_transaction()
#tx = graph.begin()

for q in commands:
    graph.run(q)
    #tx.append(q)

#tx.commit()

