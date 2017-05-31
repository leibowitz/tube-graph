import zoopla
import logging
import sys
import argparse
#import urlparse
import urllib.parse
import gmplot

proxies={'http': 'http://127.0.0.1:8989'}

parser = argparse.ArgumentParser(description='Zoopla search')

parser.add_argument('--debug',help='debug',action='store_true')
#parser.add_argument('postcode', help='Postcode area')
parser.add_argument('--latitude', type=float, required=True)
parser.add_argument('--longitude', type=float, required=True)
parser.add_argument('--radius', type=float, required=True)

args = parser.parse_args()

gmap = gmplot.GoogleMapPlotter(args.latitude, args.longitude, 13)

if args.debug:
    logging.basicConfig(level=logging.DEBUG,stream=None)

api = zoopla.api(version=1, api_key='api_key')

for listing in api.property_listings(
        #postcode=args.postcode,
        latitude=args.latitude,
        longitude=args.longitude,
        radius=args.radius,
        property_type='flats',
        minimum_price=400000,
        maximum_price=600000,
        minimum_beds=2,
        listing_status='sale',
        proxies=proxies,
        max_results=10):

    if listing.num_bathrooms != '2':
        continue
    #print("bathrooms: {}, street: {}, new home: {}, price: {}, details_url: {}".format(
    #    listing.num_bathrooms,
    #    listing.street_name,
    #    listing.new_home if listing.new_home else False,
    #    listing.price,
    #    listing.details_url,
    #    #listing.short_description,
    #    #listing.floor_plan,
    #))
    u = urllib.parse.urlparse(listing.details_url)
    #u.query = None
    details_url = u._replace(query=None).geturl()
    print(listing.listing_id, listing.latitude, listing.longitude, int(listing.price), details_url)
    marker = gmap.marker(listing.latitude, listing.longitude)
    gmap.infowindow(marker, "<a target='_blank' href='"+details_url+"'>"+listing.listing_id+"</a><br/>Price: " +str(int(listing.price)), True)



gmap.draw("mymap.html")

