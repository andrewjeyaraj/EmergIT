import pandas as pd
import folium
from folium.plugins import MarkerCluster

# Load the hospital data with geocoded locations from the CSV
data = pd.read_csv(r'C:\Users\andre\OneDrive\Documents\GitHub\EmergIT\geocoded_hospitals_with_latlon.csv')

# Verify the column names in the data
print(data.columns)

# Ensure the columns are named 'latitude' and 'longitude'
latitude_col = 'latitude' if 'latitude' in data.columns else 'Latitude'
longitude_col = 'longitude' if 'longitude' in data.columns else 'Longitude'

# Initialize map without a specific center (will use user's location)
hospital_map = folium.Map(location=[0, 0], zoom_start=2)

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

# Add HTML for radio buttons and "Find lowest wait time" button
transport_js = """
<script>
    function findLowestWaitTime() {
        var transportMode = document.querySelector('input[name="transport"]:checked').value;
        var rankedHospitals = [];
        hospitalData.sort(function(a, b) {
            return a.waiting_time - b.waiting_time;
        });

        for (var i = 0; i < hospitalData.length; i++) {
            var hospital = hospitalData[i];
            var popupContent = `<b>Hospital Name:</b> ${hospital.name}<br>
                                <b>Address:</b> ${hospital.address}<br>
                                <b>Waiting Time:</b> ${hospital.waiting_time}<br>
                                <b>Mode of Transport:</b> ${transportMode}<br>
                                <b>Website:</b> <a href="${hospital.website}" target="_blank">Visit Website</a>`;
            
            var lat = hospital.latitude;
            var lng = hospital.longitude;
            var rankedMarker = L.marker([lat, lng])
                                .addTo(map)
                                .bindPopup(popupContent)
                                .openPopup();
        }
    }
</script>

<div style="position: fixed; top: 10px; left: 10px; background-color: white; padding: 10px; border: 1px solid black; z-index: 1000;">
    <h4>Mode of Transport</h4>
    <input type="radio" id="car" name="transport" value="Car" checked>
    <label for="car">Car</label><br>
    <input type="radio" id="bicycle" name="transport" value="Bicycle">
    <label for="bicycle">Bicycle</label><br>
    <input type="radio" id="bus" name="transport" value="Bus">
    <label for="bus">Bus</label><br><br>

    <button onclick="findLowestWaitTime()">Find lowest wait time</button>
</div>
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

# Loop through each hospital entry and plot locations from the spreadsheet
hospital_data_js = "var hospitalData = ["
for index, row in data.iterrows():
    try:
        hospital_name = row['name']
        address = row['address']
        website = row['website']
        waiting_time = row['waiting_time']
        latitude = row[latitude_col]
        longitude = row[longitude_col]
        occupancy_rate = row['occupancy_rate']
        avg_wait_room = row['avg_wait_room']
        avg_stretcher_time = row['avg_stretcher_time']
        
        # Skip rows where latitude or longitude is NaN
        if pd.isna(latitude) or pd.isna(longitude):
            print(f"Skipping hospital {hospital_name} due to missing latitude/longitude")
            continue
        
        # Get color based on wait time
        marker_color = get_color(waiting_time)
        
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

# Add the user location JavaScript and transport selection JS to the map
hospital_map.get_root().html.add_child(folium.Element(user_location_js))
hospital_map.get_root().html.add_child(folium.Element(transport_js))
hospital_map.get_root().html.add_child(folium.Element(hospital_data_js))

# Save the map to an HTML file
hospital_map.save('hospital_map_with_geocoded_locations.html')

print("Map with ranking functionality saved as 'hospital_map_with_geocoded_locations.html'.")
