import csv
import json
import argparse
import ast
parser = argparse.ArgumentParser(description='Output train lines')
parser.add_argument('files', metavar='FILE', nargs='+',
                            help='CSV files')
parser.add_argument('--linkType')
parser.add_argument('--direction')
parser.add_argument('--to')
parser.add_argument('--origin')
parser.add_argument('-r', '--reverse', action="store_true")
args = parser.parse_args()

stops = []
for name in args.files:
    with open(name) as data_file:
        filereader = csv.reader(data_file, delimiter=';')
        previous_stop = None
        for line in filereader:
            if len(line) == 0:
                continue
            if previous_stop:
                if args.reverse:
                    origin = line[0]
                    destination = previous_stop[0]
                else:
                    origin = previous_stop[0]
                    destination = line[0]

                stop = {
                        'from': origin,
                        'to': destination,
                        'distanceMeters': ast.literal_eval(line[1]),
                        'durationSeconds': ast.literal_eval(line[2])
                }
                if args.linkType:
                    stop['linkType'] = args.linkType
                if args.direction:
                    stop['direction'] = args.direction
                if len(stops) != 0 or (not args.origin or args.origin == origin):
                    stops.append(stop)
                if args.to and args.to == destination:
                    break
            previous_stop = line
if args.reverse:
    stops.reverse()
print(json.dumps(stops))

