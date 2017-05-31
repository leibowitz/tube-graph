from fastkml import kml
import json
import csv
import ast
import sys

stations = {}
#with open('./tube-data2.json') as data_file:
#    data = json.load(data_file)
#    for station in data['stations']:
#        stations[station['name']] = station

with open('./csv_stations/trams.txt') as data_file:
    for station in data_file.readlines():
        station = station.strip()
        stations[station] = {'name': station}

with open('./csv_stations/station.csv') as data_file:
    filereader = csv.reader(data_file, delimiter=';')
    for line in filereader:
        if len(line) < 5 or len(line[0]) == 0:
            continue
        if line[0] in stations:
            zones = line[4].split(',')
            zones = [int(zone) if isinstance(zone, int) or zone.isdigit() else zone for zone in zones]
            #zones = ast.literal_eval('['+str(line[4])+']')
            stations[line[0]]["zones"] = zones

k = kml.KML()
with open('./London stations_utf8.kml') as data_file:
    d = data_file.read()
    k.from_string(d.encode('utf-8'))

output = []
for doc in k.features():
    for placemark in doc.features():
        if placemark.name not in stations:
            continue
        station = {
                "name": placemark.name,
                "type": "tram",
                #"description": "",
                "lat": placemark.geometry.y,
                "lng": placemark.geometry.x
            }
        if "zones" in stations[placemark.name]:
            station["zones"] = stations[placemark.name]['zones']
        #print(placemark.name, placemark.geometry.y, placemark.geometry.x)
        output.append(station)

        #print(placemark, placemark.name)
        #print(placemark.description)
        #for element in placemark.etree_element().iter():
        #    if element.tag != '{http://www.opengis.net/kml/2.2}description':
        #        continue
        #    print(dir(element))
        #    print('1', element.tag)
        #    print(element, dir(element))
        #sys.exit(1)
print(json.dumps(output))
