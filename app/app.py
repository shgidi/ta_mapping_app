#!flask/bin/python
import sys
from flask import Flask, render_template, request, redirect, Response, jsonify
import random, json
import folium
from folium.plugins import MarkerCluster
import numpy as np
# init the location searcher
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="app")
from geopy import distance

app = Flask(__name__)

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

def init_map():

    with open('app/data.json') as outfile:
        data = json.load(outfile)

    center = list(np.mean([[i['lat'],i['lon']] for i in data],axis=0))
    map_1 = folium.Map(location=center, zoom_start=13,tiles=None,width=1000,height=500)
    map_1.add_tile_layer() #default alayer
    # data as json ~!@2
    data_sites = [{"coordinates":[i['lat'],i['lon']],'name':i['name'],'address':i['address'],'desc':i['desc']}
            for i in data]
    # create the markers
    feature_group_active = folium.FeatureGroup(name='Active')
    
    marker_cluster_active = MarkerCluster()
    
    # add markers
    for site in data_sites:
        marker_active = folium.Marker(site["coordinates"], popup=site["name"]+'-\n'+site['desc']
        	,icon = folium.Icon(color='green',icon='ok-sign'))
        marker_cluster_active.add_child(marker_active)
    
    # ad top maps
    map_1.add_child(marker_cluster_active)
    return map_1

map_1 = init_map()

@app.route('/')
def output():
	# serve index template
	global map_1
	print('running mains')
	return render_template('index.html', map=map_1._repr_html_())

def calc_route(start, data, time =1):
	"""
	# template for route calclator
	start: start dict (lat, lon, address)
	data: data list
	time: time for trip. 2km per hour
	"""
	location = start
	route=[]
	valids = np.ones(len(data),dtype='int')
	route.append(location)
	while calc_route_len(route)<time*2:
	    name = find_closest(location, data, valids)
	    id = np.where(name==np.array([i['name'] for i in data]))[0][0]
	    valids[id] = 0
	    route.append(data[id])
	route.append(start)
	return route
	print(calc_route_len(route))

def find_closest(root, data, valids):
	# find closes point function
	# returns name
    dists = []
    names = []
    for point in np.array(data)[valids.astype('bool')]:
        dists.append(distance.distance([point['lat'],point['lon']],[root['lat'],root['lon']]))
        names.append(point['name'])
    id = np.argmin(dists)
    return names[id] 

def calc_route_len(route):
    length = 0
    start = route[0]
    end = route[-1]
    length += distance.distance([start['lat'],start['lon']],[end['lat'],end['lon']]).km
    for point in route[1:]:
        length += distance.distance([start['lat'],start['lon']],[point['lat'],point['lon']]).km
        start = point # todo: verify its byval and not by ref VV
    return length

def update_map(coords):
	# add marker to map
	#global map_1
	map_1 = init_map()
	folium.Marker([coords[0][0], coords[0][1]],popup= 'start').add_to(map_1)
	folium.PolyLine(coords).add_to(map_1)
	# map_1.save('app/static/test_map.html')
	
	return map_1

@app.route('/address_search', methods = ['POST'])
def address_search():
	#global map_1
	# gets address and draws route
	#
	with open('app/data.json') as outfile:
		data = json.load(outfile)

	if request.form['address']:
		address = request.form['address']+' תל אביב'
		time =  int(request.form['time'])

		print(address[::-1])
		location = geolocator.geocode(address+' תל אביב')
		if location:
			start = {'lat':location.latitude,'lon':location.longitude,'address':address,'name':'נקודת מוצא'}

		route = calc_route(start, data, time)
		print('route is', route)
		map_1 = update_map([[r['lat'],r['lon']] for r in route])
		print('updating')
		return jsonify({'route':['המסלול שלך לשעות הקרובות הוא: <br>']+[i['name']+'-'+i['address']+'<br>' for i in route], 'map':map_1._repr_html_()})
	else:
		return jsonify('your request is empty')

if __name__ == '__main__':
	if "serve" in sys.argv: app.run(debug=True, host='0.0.0.0', port='8080')