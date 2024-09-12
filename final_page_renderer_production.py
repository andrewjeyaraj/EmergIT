# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 18:41:12 2024

@author: andre
"""

import pandas as pd
import folium
from folium.plugins import MarkerCluster
from math import radians, cos, sin, sqrt, atan2
import numpy as np
import os

# Get the current directory (where the script is located)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load the hospital data (relative path)
data_path = os.path.join(current_dir, 'geocoded_hospitals_with_latlon.csv')
data = pd.read_csv(data_path)

# Function to calculate distance using the Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Function to get color based on waiting time
def get_color(waiting_time):
    try:
        wait_minutes = int(waiting_time.split(':')[0])  # Get hours from 'hh:mm' format
        if wait_minutes < 2:
            return 'green'
        elif 2 <= wait_minutes <= 5:
            return 'orange'
        else:
            return 'red'
    except:
        return 'blue'  # default color if time parsing fails

# Initialize the map
hospital_map = folium.Map(location=[46.8139, -71.2082], zoom_start=6)  # Center on Quebec City
marker_cluster = MarkerCluster().add_to(hospital_map)

# Add hospital pins with color coding based on waiting time
for index, row in data.iterrows():
    latitude = row['latitude']
    longitude = row['longitude']
    
    # Skip rows with NaN values for latitude or longitude
    if np.isnan(latitude) or np.isnan(longitude):
        #print(f"Skipping hospital {row['name']} due to missing location data.")
        continue
    
    hospital_name = row['name']
    address = row['address']
    website = row['website']
    waiting_time = row['waiting_time']
    
    marker_color = get_color(waiting_time)
    
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
        popup=folium.Popup(popup_content, max_width=250),
        icon=folium.Icon(color=marker_color)
    ).add_to(marker_cluster)

# Add JavaScript to get user's location and calculate the nearest hospital
user_location_js = """
<script>
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var userLat = position.coords.latitude;
            var userLon = position.coords.longitude;
            document.getElementById("userLat").value = userLat;
            document.getElementById("userLon").value = userLon;
            var userMarker = L.marker([userLat, userLon]).addTo(map).bindPopup('You are here!').openPopup();
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
function findNearestHospital() {
    var transportMode = document.querySelector('input[name="transport"]:checked').value;
    var userLat = parseFloat(document.getElementById("userLat").value);
    var userLon = parseFloat(document.getElementById("userLon").value);
    
    var radius = 0;
    if (transportMode === "Car") {
        radius = 15; // 15 km for car
    } else if (transportMode === "Bicycle") {
        radius = 2; // 2 km for bicycle
    } else if (transportMode === "Bus") {
        radius = 5; // 5 km for bus
    }

    // Find the nearest hospital within the radius
    var nearestHospital = null;
    var minWaitTime = Number.MAX_VALUE;
    var hospitalData = """ + str(data.dropna(subset=['latitude', 'longitude']).to_dict(orient="records")) + """;
    
    hospitalData.forEach(function(hospital) {
        var distance = haversine(userLat, userLon, hospital.latitude, hospital.longitude);
        if (distance <= radius) {
            var waitTime = parseInt(hospital.waiting_time.split(":")[0]);  // Extract hours
            if (waitTime < minWaitTime) {
                minWaitTime = waitTime;
                nearestHospital = hospital;
            }
        }
    });

    if (nearestHospital) {
        document.getElementById("output").innerHTML = 
        "Nearest hospital: <b>" + nearestHospital.name + "</b> <br>Address: " + nearestHospital.address + "<br>Wait time: " + nearestHospital.waiting_time;
    } else {
        document.getElementById("output").innerHTML = "No hospitals found within " + radius + " km radius.";
    }
}
</script>
"""

# Add input elements to hold user location
input_elements = """
<input type="hidden" id="userLat" value="0">
<input type="hidden" id="userLon" value="0">
"""

# Add transport selection panel with results display area to the map
panel = """
<div style="position: fixed; bottom: 10px; left: 10px; background-color: white; padding: 20px; width: 300px; border: 1px solid black; z-index:9999;">
    <h4>Mode of Transport</h4>
    <input type="radio" id="car" name="transport" value="Car" checked>
    <label for="car">Car</label><br>
    <input type="radio" id="bicycle" name="transport" value="Bicycle">
    <label for="bicycle">Bicycle</label><br>
    <input type="radio" id="bus" name="transport" value="Bus">
    <label for="bus">Bus</label><br><br>

    <button onclick="findNearestHospital()">Find lowest wait time</button>

    <div id="output" style="margin-top: 10px;z-index:9999;">
        <!-- Output will be displayed here -->
    </div>
</div>
"""

# Add everything to the map
hospital_map.get_root().html.add_child(folium.Element(input_elements))
hospital_map.get_root().html.add_child(folium.Element(panel))
hospital_map.get_root().html.add_child(folium.Element(user_location_js))
hospital_map.get_root().html.add_child(folium.Element(transport_js))

# Save the map to an HTML file (relative path)
output_map_path = os.path.join(current_dir, 'hospital_map_with_nearest_hospital_panel.html')
hospital_map.save(output_map_path)
#print(f"Map with nearest hospital functionality saved as '{output_map_path}'.")
