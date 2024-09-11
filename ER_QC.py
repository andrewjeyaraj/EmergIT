# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 15:48:44 2024

@author: andre
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import csv
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Base URL
base_url = 'https://www.quebec.ca/en/health/health-system-and-services/service-organization/quebec-health-system-and-its-services/situation-in-emergency-rooms-in-quebec?id=24981&tx_solr%5Blocation%5D=&tx_solr%5Bpt%5D=&tx_solr%5Bsfield%5D=geolocation_location&tx_solr%5Bpage%5D='

# Path to your WebDriver
driver_path = r'C:\Users\andre\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'
options = Options()
options.add_argument("--headless")
# Create a Service object and pass it to the Chrome WebDriver
service = Service(driver_path)
driver = webdriver.Chrome(service=service,options=options)

# Function to extract data from a page
def extract_hospital_data(page_num):
    url = base_url + str(page_num)
    driver.get(url)
    time.sleep(3)  # Wait for the page to load
    
    hospitals = []
    
    # Identifying all hospital sections
    for i in range(1, len(driver.find_elements(By.CSS_SELECTOR, 'div.hospital_element')) + 1):
        try:
            name = driver.find_element(By.XPATH, f"//ul/div[{i}]/ul/li[1]/div[1]/div[1]").text
            address = driver.find_element(By.XPATH, f"//ul/div[{i}]/ul/li[1]/div[1]/div[2]").text
            website_element = driver.find_element(By.XPATH, f"//ul/div[{i}]/ul/li[1]/div[1]/div[3]/a")
            website = website_element.get_attribute('href') if website_element else 'N/A'
            waiting_time = driver.find_element(By.XPATH, f"//ul/div[{i}]/ul/li[2]/div[2]/span").text
            num_waiting = driver.find_element(By.XPATH, f"//ul/div[{i}]/ul/li[3]/div[2]/span").text
            total_people = driver.find_element(By.XPATH, f"//ul/div[{i}]/ul/li[4]/div[2]/span").text
            occupancy_rate = driver.find_element(By.XPATH, f"//ul/div[{i}]/ul/li[5]/div[2]/span").text
            avg_wait_room = driver.find_element(By.XPATH, f"//ul/div[{i}]/ul/li[6]/div[2]/span").text
            avg_stretcher_time = driver.find_element(By.XPATH, f"//ul/div[{i}]/ul/li[7]/div[2]/span").text

            hospitals.append({
                'name': name,
                'address': address,
                'website': website,
                'waiting_time': waiting_time,
                'num_waiting': num_waiting,
                'total_people': total_people,
                'occupancy_rate': occupancy_rate,
                'avg_wait_room': avg_wait_room,
                'avg_stretcher_time': avg_stretcher_time
            })
        except Exception as e:
            print(f"Error extracting data for hospital {i} on page {page_num}: {e}")
    
    return hospitals

# Function to scrape hospitals across multiple pages
def scrape_hospitals(max_pages):
    all_hospital_data = []
    
    for page_num in range(1, max_pages + 1):
        hospitals = extract_hospital_data(page_num)
        if hospitals:  # Only extend if hospitals are found
            all_hospital_data.extend(hospitals)
        else:
            break
    
    return all_hospital_data

# Example: Scrape data from the first 12 pages (you can adjust the number as necessary)
hospital_data = scrape_hospitals(12)

# Close the Selenium driver after scraping
driver.quit()

# Check if hospital data is available before exporting
if hospital_data:
    # Export data to CSV
    keys = hospital_data[0].keys()
    with open('hospital_data.csv', 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(hospital_data)

    # Print confirmation
    print(f"Data for {len(hospital_data)} hospitals exported to 'hospital_data.csv'")
else:
    print("No hospital data found.")
