# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 16:12:41 2024

@author: andre
"""

import pandas as pd
import re

# Load the CSV file
data = pd.read_csv(r'C:\Users\andre\OneDrive\Documents\GitHub\EmergIT\hospital_data.csv')

# Define a function to append "Quebec" if it's missing
def append_quebec_to_address(address):
    # Check if "Quebec" is already in the address
    if "Quebec" not in address:
        # Find the part of the address before the postal code (a string of 6 characters like 'G1V 4G2')
        postal_code_match = re.search(r'\b\w\d\w \d\w\d\b', address)
        if postal_code_match:
            postal_code = postal_code_match.group()
            # Append "Quebec" right before the postal code
            address = address.replace(postal_code, "Quebec, " + postal_code)
    return address

# Apply the function to the 'address' column
data['address'] = data['address'].apply(append_quebec_to_address)

# Save the updated data back to a CSV file
data.to_csv('hospital_data_with_quebec.csv', index=False)

print("Addresses updated and saved to 'hospital_data_with_quebec.csv'")
