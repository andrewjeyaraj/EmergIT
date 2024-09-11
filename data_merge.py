# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 18:43:27 2024

@author: andre
"""

import pandas as pd
import os

# Get the current directory (where the script is located)
current_dir = os.path.dirname(os.path.abspath(__file__))

# File paths
hospital_data_path = os.path.join(current_dir, 'hospital_data.csv')
geocoded_hospitals_path = os.path.join(current_dir, 'geocoded_hospitals_with_latlon.csv')

# Read hospital data (contains timing information)
hospital_data = pd.read_csv(hospital_data_path)

# Read geocoded hospital data (contains name, address, lat/lon, and link)
geocoded_hospitals = pd.read_csv(geocoded_hospitals_path)

# Assuming 'name' is the common column between both files
# If the column name is different, adjust it accordingly in the merge operation

# Merge the two dataframes on the 'name' column
merged_data = pd.merge(geocoded_hospitals, hospital_data[['name', 'waiting_time']], on='name', how='left')

# Save the updated data to a new CSV file (or overwrite the existing one)
output_path = os.path.join(current_dir, 'geocoded_hospitals_with_latlon.csv')
merged_data.to_csv(output_path, index=False)

print(f"Data merged successfully. Output saved to {output_path}")
