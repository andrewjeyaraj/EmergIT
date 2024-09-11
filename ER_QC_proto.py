# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 14:45:11 2024

@author: andre
"""

from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# Base URL (update with the actual hospital URL)
base_url = 'https://www.quebec.ca/en/health/health-system-and-services/service-organization/quebec-health-system-and-its-services/situation-in-emergency-rooms-in-quebec?id=24981&tx_solr%5Blocation%5D=&tx_solr%5Bpt%5D=&tx_solr%5Bsfield%5D=geolocation_location&tx_solr%5Bpage%5D='

# Path to your WebDriver (ChromeDriver, GeckoDriver, etc.)
driver_path = r'C:\Users\andre\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'  # Replace with your actual path

# Create a Service object and pass it to the Chrome WebDriver
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

def extract_hospital_data(page_num):
    url = base_url + str(page_num)
    driver.get(url)
    
    # Wait for the JavaScript to load (adjust the time if necessary)
    time.sleep(3)

    # Locate hospital entries by container div
    hospitals = driver.find_elements(By.XPATH, "//ul/div")  # Modify this based on your container's structure
    hospital_data = []

    for i, hospital in enumerate(hospitals, start=1):
        try:
            # XPaths for name, address, and website
            name_xpath = f".//ul/li[1]/div[1]/div[1]"  # Hospital name
            address_xpath = f".//ul/li[1]/div[1]/div[2]"  # Hospital address
            website_xpath = f".//ul/li[1]/div[1]/div[3]/a/span/img"  # Hospital website

            # Extracting the fields
            name = hospital.find_element(By.XPATH, name_xpath).text.strip() if hospital.find_element(By.XPATH, name_xpath) else "N/A"
            address = hospital.find_element(By.XPATH, address_xpath).text.strip() if hospital.find_element(By.XPATH, address_xpath) else "N/A"
            website = hospital.find_element(By.XPATH, website_xpath).get_attribute('src') if hospital.find_element(By.XPATH, website_xpath) else "N/A"

            # Other fields (waiting time, num waiting, etc.)
            waiting_time = hospital.find_element(By.XPATH, ".//ul/li[2]/div[2]/span").text.strip()
            num_waiting = hospital.find_element(By.XPATH, ".//ul/li[3]/div[2]/span").text.strip()
            total_people = hospital.find_element(By.XPATH, ".//ul/li[4]/div[2]/span").text.strip()
            occupancy_rate = hospital.find_element(By.XPATH, ".//ul/li[5]/div[2]/span").text.strip()
            avg_wait_room = hospital.find_element(By.XPATH, ".//ul/li[6]/div[2]/span").text.strip()
            avg_stretcher_time = hospital.find_element(By.XPATH, ".//ul/li[7]/div[2]/span").text.strip()

            # Append the data as a dictionary
            hospital_data.append({
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
    
    return hospital_data

# Function to scrape multiple pages
def scrape_hospitals(pages):
    all_hospital_data = []
    for page_num in range(1, pages + 1):
        hospitals = extract_hospital_data(page_num)
        all_hospital_data.extend(hospitals)
    return all_hospital_data

# Example: Scrape data from pages 1 to 3
hospital_data = scrape_hospitals(3)

# Close the Selenium driver after scraping
driver.quit()

# Display or save the results
for hospital in hospital_data:
    print(hospital)
