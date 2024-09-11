# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 14:32:36 2024

@author: andre
"""

import requests

# Base URL with placeholder for page number
base_url = 'https://www.quebec.ca/en/health/health-system-and-services/service-organization/quebec-health-system-and-its-services/situation-in-emergency-rooms-in-quebec?id=24981&tx_solr%5Blocation%5D=&tx_solr%5Bpt%5D=&tx_solr%5Bsfield%5D=geolocation_location&tx_solr%5Bpage%5D='

# Loop through pages 1 to 12 and fetch the HTML content
for page_num in range(1, 12):
    url = base_url + str(page_num)
    response = requests.get(url)
    
    if response.status_code == 200:
        print(f"Page {page_num} content fetched successfully")
        # Do something with the page content, e.g., save or parse
        page_content = response.text
        # You can print or save the page content for later inspection if needed
        # print(page_content)  # Uncomment if you want to see raw HTML
    else:
        print(f"Failed to fetch page {page_num}")
