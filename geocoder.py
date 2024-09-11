# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 16:01:04 2024

@author: andre
"""

import pandas as pd
import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from time import sleep

# Load the hospital data from the CSV
data = pd.read_csv(r'C:\Users\andre\OneDrive\Documents\GitHub\EmergIT\hospital_data.csv')

# Initialize map without a specific center (will use user's location)
hospital_map = folium.Map(location=[0, 0], zoom_start=2)

# Initialize Nominatim geocoder
geolocator = Nominatim(user_agent="hospital_locator")

# Add JavaScript to get user's location and update the map
user_location_js = """
<script>
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var lat = position.coords.latitude;
            var lng = position.coords.longitude;
            var userLocation = L.latLng(lat, lng);
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

# Initialize MarkerCluster for grouping pins
marker_cluster = MarkerCluster().add_to(hospital_map)

# Loop through each hospital entry and geocode addresses
for index, row in data.iterrows():
    try:
        hospital_name = row['name']
        address = row['address']
        website = row['website']
        waiting_time = row['waiting_time']
        occupancy_rate = row['occupancy_rate']
        avg_wait_room = row['avg_wait_room']
        avg_stretcher_time = row['avg_stretcher_time']
        
        # Get color based on wait time
        marker_color = get_color(waiting_time)
        
        # Geocode the address to get latitude and longitude
        location = geolocator.geocode(address)
        if location:
            latitude = location.latitude
            longitude = location.longitude
            
            # Create popup content
            popup_content = f"""
            <b>Hospital Name:</b> {hospital_name}<br>
            <b>Address:</b> {address}<br>
            <b>Waiting Time:</b> {waiting_time}<br>
            <b>Occupancy Rate:</b> {occupancy_rate}<br>
            <b>Average Wait Room Time:</b> {avg_wait_room}<br>
            <b>Average Stretcher Time:</b> {avg_stretcher_time}<br>
            <b>Website:</b> <a href="{website}" target="_blank">Visit Website</a>
            """
            
            # Add marker to the map
            folium.Marker(
                location=[latitude, longitude],
                popup=folium.Popup(popup_content, max_width=250),
                icon=folium.Icon(color=marker_color)
            ).add_to(marker_cluster)
            
            print(f"Added {hospital_name} at {latitude}, {longitude}")
        else:
            print(f"Geocoding failed for address: {address}")
        
        # Sleep to respect Nominatim's usage policy
        sleep(1)

    except Exception as e:
        print(f"Error adding hospital {row['name']} to map: {e}")

# Add the user location JavaScript to the map
hospital_map.get_root().html.add_child(folium.Element(user_location_js))

# Save the map to an HTML file
hospital_map.save('hospital_map_with_geocoded_locations.html')

# Optionally, display the map directly in a Jupyter Notebook if using one
hospital_map
