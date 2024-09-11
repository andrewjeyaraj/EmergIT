# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 18:45:57 2024

@author: andre
"""

import os
import subprocess

# Get the current directory (where the script is located)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the paths to the scripts
er_qc_path = os.path.join(current_dir, 'ER_QC_production.py')
data_merge_path = os.path.join(current_dir, 'data_merge.py')
final_renderer_path = os.path.join(current_dir, 'final_page_renderer_production.py')

# Function to execute a script and handle errors
def run_script(script_path):
    try:
        result = subprocess.run(['python', script_path], capture_output=True, text=True)
        print(f"Running {script_path}...")
        print(result.stdout)  # Print the output of the script
        if result.stderr:
            print(f"Error in {script_path}: {result.stderr}")
    except Exception as e:
        print(f"Failed to run {script_path}: {str(e)}")

# Step 1: Run ER_QC_production.py
run_script(er_qc_path)

# Step 2: Run data_merge.py
run_script(data_merge_path)

# Step 3: Run final_page_renderer_production.py
run_script(final_renderer_path)
