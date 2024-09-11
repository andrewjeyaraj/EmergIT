# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 17:39:13 2024

@author: andre
"""

import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import subprocess
import os

# Function to run the scraper script
def run_scraper():
    scraper_file = '/path/to/ER_QC.py'  # Update with the correct path
    subprocess.run(['python', scraper_file], check=True)
    st.success("Scraper script has been run successfully!")

# Function to update waiting times in the geocoded hospitals file
def update_wait_times():
    # Load the scraped data CSV with the waiting times (ensure it is updated in ER_QC.py output)
    scraped_csv = '/path/to/scraped_wait_times.csv'  # Update with the correct path
    scraped_data = pd.read_csv(scraped_csv)

    # Load the geocoded hospitals CSV
    hospitals_csv = '/path/to/geocoded_hospitals_with_latlon.csv'  # Update with the correct path
    hospital_data = pd.read_csv(hospitals_csv)

    # Update the waiting times in the geocoded hospitals CSV based on names or IDs
    for index, row in hospital_data.iterrows():
        matching_scraped_data = scraped_data[scraped_data['name'] == row['name']]
        if not matching_scraped_data.empty:
            hospital_data.loc[index, 'waiting_time'] = matching_scraped_data['waiting_time'].values[0]

    # Save the updated hospital data
    hospital_data.to_csv(hospitals_csv, index=False)
    st.success("Waiting times updated successfully!")

# Function to generate the map
def generate_map():
    # Load the updated geocoded hospitals CSV
    hospitals_csv = '/path/to/geocoded_hospitals_with_latlon.csv'  # Update with the correct path
    hospital_data = pd.read_csv(hospitals_csv)

    # Initialize the map
    hospital_map = folium.Map(location=[46.8139, -71.2082], zoom_start=6)  # Centered on Quebec

    # Initialize MarkerCluster for grouping pins
    marker_cluster = MarkerCluster().add_to(hospital_map)

    # Add hospitals to the map
    for index, row in hospital_data.iterrows():
        if pd.notna(row['latitude']) and pd.notna(row['longitude']):
            # Create popup content
            popup_content = f"""
            <b>Hospital Name:</b> {row['name']}<br>
            <b>Address:</b> {row['address']}<br>
            <b>Waiting Time:</b> {row['waiting_time']}<br>
            <b>Website:</b> <a href="{row['website']}" target="_blank">Visit Website</a>
            """
            
            # Add marker to the map
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_content, max_width=250),
                icon=folium.Icon(color='blue')
            ).add_to(marker_cluster)

    # Display map in Streamlit
    st_data = st_folium(hospital_map, width=725)
    st.success("Map generated successfully!")

# Streamlit app layout
st.title("Hospital Wait Time Monitor")

# Button to run the scraper
if st.button("Run Scraper"):
    run_scraper()

# Button to update waiting times
if st.button("Update Waiting Times"):
    update_wait_times()

# Button to generate the map
if st.button("Generate Map"):
    generate_map()
