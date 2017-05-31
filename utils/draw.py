import gmplot

gmap = gmplot.GoogleMapPlotter(10, 10, 16)

gmap.marker(10, 10)

gmap.draw("mymap.html")
