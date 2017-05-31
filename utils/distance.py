from haversine import haversine
import argparse
import sys
parser = argparse.ArgumentParser(description='Process haversine')
parser.add_argument('locations', metavar='L', type=float, nargs='+',
                            help='floats')
args = parser.parse_args()
h = haversine(args.locations[:2], args.locations[2:])
print(h)
