from py2neo import Graph

max_time = 2700

graph = Graph("http://neo4j:passwd@localhost:7474/db/data/")
for record in graph.run("""
        
// find tube stations within 1km of E2 8DD (near Kingsland Road)
with 51.528012 as lat, -0.0793786 as lng
CALL spatial.withinDistance('tube-stations',{longitude:lng,latitude:lat},1.5) yield node as start
WITH start, 2 * 6371 * asin(sqrt(haversin(radians(lat - start.latitude)) + cos(radians(lat)) * cos(radians(start.latitude)) * haversin(radians(lng - start.longitude)))) as distance // distance is between station and original lat/lng in km
MATCH (end:Station)
CALL apoc.algo.dijkstra(start, end, 'ROUTE>', 'time') YIELD path, weight
WHERE length(path) > 0
WITH path, start, end, distance, distance*600 + weight as totaltime, length(path) as stops, reduce(a=[], x IN [x in nodes(path) | x.line] | CASE WHEN x is not null and NOT x IN a THEN a + x ELSE a END) as lines // distance*600 because on average it takes about 10 min to walk 1km
WHERE length(lines) < 3 // 1 line change maximum
AND totaltime < 2400 // maximum 40 min
AND filter(x IN end.zones WHERE 2 in x or 3 in x or 4 in x or 5 in x) // in zone 2, 3, 4 or 5
// To get only end stations and average total time, use this
RETURN distinct end, avg(totaltime) as time
ORDER BY time

        """):
        max_walk_time = max_time - record['time']
        distance_walk_km = max_walk_time / 600 # in km
        distance_walk_miles = distance_walk_km / 1.6
        print(record['end']['name'], distance_walk_miles, max_walk_time, record['time'], record['end']['latitude'], record['end']['longitude'])
        print("python run.py", "--latitude", record['end']['latitude'], "--longitude", record['end']['longitude'], "--radius", distance_walk_miles * 1.5, "#", record['end']['name'])
