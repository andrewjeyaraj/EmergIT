# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 17:09:38 2024

@author: andre
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 16:01:04 2024

@author: andre
"""

import pandas as pd
import folium
from folium.plugins import MarkerCluster
import requests
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Load the hospital data from the CSV
data = pd.read_csv(r'C:\Users\andre\OneDrive\Documents\GitHub\EmergIT\geocoded_hospitals_with_latlon.csv')

# Initialize map without a specific center (will use user's location)
hospital_map = folium.Map(location=[46.8139, -71.2082], zoom_start=6)  # Centering on Quebec

# OpenRouteService API key (Replace 'YOUR_API_KEY' with your actual key)
ORS_API_KEY = '5b3ce3597851110001cf62485fc961b9175542a1b43b85cf7b65a6a7'

# ORS API endpoint
ORS_API_URL = 'https://api.openrouteservice.org/v2/directions'

# Add JavaScript to get user's location and update the map
user_location_js = """
<script>
var userLatitude;
var userLongitude;
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            userLatitude = position.coords.latitude;
            userLongitude = position.coords.longitude;
            var userLocation = L.latLng(userLatitude, userLongitude);
            map.setView(userLocation, 10); // Center the map on user's location
            var userMarker = L.marker(userLocation).addTo(map).bindPopup('You are here!').openPopup();
        });
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}
getLocation();
</script>
"""

# Add HTML for radio buttons and "Find lowest wait time" button
transport_js = """
<script>
    async function findLowestWaitTime() {
        var transportMode = document.querySelector('input[name="transport"]:checked').value;
        var mode;
        if (transportMode === 'Car') {
            mode = 'driving-car';
        } else if (transportMode === 'Bicycle') {
            mode = 'cycling-regular';
        } else if (transportMode === 'Bus') {
            mode = 'driving-hgv';  // Use driving for buses
        }

        var userLat = userLatitude;
        var userLng = userLongitude;

        var hospitalsWithRoutes = [];

        // Call the server-side script to get route data for each hospital
        for (var i = 0; i < hospitalData.length; i++) {
            var hospital = hospitalData[i];
            var routeData = await getRouteDistance(userLat, userLng, hospital.latitude, hospital.longitude, mode);
            
            if (routeData.distance <= 15000 && mode === 'driving-car' || 
                routeData.distance <= 5000 && mode === 'cycling-regular' || 
                routeData.distance <= 2000 && mode === 'driving-hgv') {
                
                hospital.routeDistance = routeData.distance;
                hospitalsWithRoutes.push(hospital);
            }
        }

        // Sort hospitals by waiting time within the distance radius
        hospitalsWithRoutes.sort(function(a, b) {
            return a.waiting_time.localeCompare(b.waiting_time);
        });

        // Display sorted hospitals
        var result = '';
        for (var i = 0; i < hospitalsWithRoutes.length; i++) {
            var hospital = hospitalsWithRoutes[i];
            result += '<b>' + (i + 1) + '. ' + hospital.name + '</b>, Waiting Time: ' + hospital.waiting_time + ', Route Distance: ' + (hospital.routeDistance / 1000).toFixed(2) + ' km<br>';
        }

        document.getElementById('resultBar').innerHTML = result || 'No hospitals found within the selected radius.';
    }

    // Function to call the server and get the route distance using ORS API
    async function getRouteDistance(lat1, lon1, lat2, lon2, mode) {
        const response = await fetch(`/get_route_distance?lat1=${lat1}&lon1=${lon1}&lat2=${lat2}&lon2=${lon2}&mode=${mode}`);
        const data = await response.json();
        return data;
    }
</script>

<div style="position: fixed; bottom: 100px; left: 10px; background-color: white; padding: 10px; border: 1px solid black; z-index: 1000;">
    <h4>Mode of Transport</h4>
    <input type="radio" id="car" name="transport" value="Car" checked>
    <label for="car">Car</label><br>
    <input type="radio" id="bicycle" name="transport" value="Bicycle">
    <label for="bicycle">Bicycle</label><br>
    <input type="radio" id="bus" name="transport" value="Bus">
    <label for="bus">Bus</label><br><br>

    <button onclick="findLowestWaitTime()">Find lowest wait time</button>
</div>

<div id="resultBar" style="position: fixed; bottom: 0px; left: 0px; width: 100%; background-color: white; padding: 10px; border-top: 1px solid black; z-index: 1000;">
    Results will be displayed here.
</div>
"""

# Function to call the ORS API to get route distance
def get_route_distance(lat1, lon1, lat2, lon2, mode):
    try:
        coords = [[lon1, lat1], [lon2, lat2]]
        request_url = f"{ORS_API_URL}/{mode}/geojson"
        headers = {
            'Authorization': ORS_API_KEY,
            'Content-Type': 'application/json'
        }
        body = {
            "coordinates": coords
        }
        response = requests.post(request_url, json=body, headers=headers)
        route_data = response.json()

        # Extract route distance (in meters)
        distance = route_data['features'][0]['properties']['segments'][0]['distance']
        return {'distance': distance}
    except Exception as e:
        return {'distance': float('inf'), 'error': str(e)}

# Flask endpoint to handle route distance requests
@app.route('/get_route_distance')
def get_route_distance_endpoint():
    lat1 = request.args.get('lat1')
    lon1 = request.args.get('lon1')
    lat2 = request.args.get('lat2')
    lon2 = request.args.get('lon2')
    mode = request.args.get('mode')
    return jsonify(get_route_distance(float(lat1), float(lon1), float(lat2), float(lon2), mode))

# Add the user location JavaScript, transport selection JS, and hospital data to the map
hospital_map.get_root().html.add_child(folium.Element(user_location_js))
hospital_map.get_root().html.add_child(folium.Element(transport_js))

# Initialize MarkerCluster for grouping pins
marker_cluster = MarkerCluster().add_to(hospital_map)

hospital_data_js = "var hospitalData = ["
for index, row in data.iterrows():
    try:
        hospital_name = row['name']
        address = row['address']
        website = row['website']
        waiting_time = row['waiting_time']
        latitude = row['latitude']
        longitude = row['longitude']

        # Create popup content
        popup_content = f"""
        <b>Hospital Name:</b> {hospital_name}<br>
        <b>Address:</b> {address}<br>
        <b>Waiting Time:</b> {waiting_time}<br>
        <b>Website:</b> <a href="{website}" target="_blank">Visit Website</a>
        """

        # Add marker to the map
        folium.Marker(
            location=[latitude, longitude],
            popup=folium.Popup(popup_content, max_width=250)
        ).add_to(marker_cluster)

        # Add data to JavaScript array
        hospital_data_js += f"""
        {{
            name: "{hospital_name}",
            address: "{address}",
            waiting_time: "{waiting_time}",
            latitude: {latitude},
            longitude: {longitude},
            website: "{website}"
        }},"""
    except Exception as e:
        print(f"Error adding hospital {row['name']} to map: {e}")

hospital_data_js += "];"
hospital_map.get_root().html.add_child(folium.Element(f"<script>{hospital_data_js}</script>"))

# Save the map to an HTML file
hospital_map.save('hospital_map_with_routing.html')

print("Map with routing functionality saved as 'hospital_map_with_routing.html'.")

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
