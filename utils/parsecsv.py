import csv
import json

stations = {}
#with open('./tube-data2.json') as data_file:
#    data = json.load(data_file)
#    for station in data['stations']:
#        stations[station['name']] = station

with open('./csv_stations/stations.txt') as data_file:
    for station in data_file.readlines():
        station = station.strip()
        stations[station] = station

new_stations = []
with open('./csv_stations/station.csv') as data_file:
    filereader = csv.reader(data_file, delimiter=';')
    for line in filereader:
        if len(line) == 0:
            continue
        station = {
                "name": line[0],
            }
        if line[0] in stations:
            print(line)
            new_stations.append(station)
        #print(station)
print(json.dumps(new_stations))
