import streamlit as st
import os
import subprocess

# Get the current directory (where the script is located)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the paths to the scripts and HTML file
er_qc_path = os.path.join(current_dir, 'ER_QC_production.py')
data_merge_path = os.path.join(current_dir, 'data_merge.py')
final_renderer_path = os.path.join(current_dir, 'final_page_renderer_production.py')
map_html_path = os.path.join(current_dir, 'hospital_map_with_nearest_hospital_panel.html')

# Function to execute a script and handle errors
def run_script(script_path):
    try:
        result = subprocess.run(['python', script_path], capture_output=True, text=True)
        st.write(f"Running {script_path}...")
        st.write(result.stdout)  # Print the output of the script
        if result.stderr:
            st.error(f"Error in {script_path}: {result.stderr}")
    except Exception as e:
        st.error(f"Failed to run {script_path}: {str(e)}")

# Streamlit app starts here
st.title('Hospital Map Loader')

# Button to trigger the process of loading the map
if st.button('Load Map'):
    # Step 1: Run ER_QC_production.py
    run_script(er_qc_path)

    # Step 2: Run data_merge.py
    run_script(data_merge_path)

    # Step 3: Run final_page_renderer_production.py to generate the map
    run_script(final_renderer_path)

    # Step 4: Check if the HTML file exists and display the map
    if os.path.exists(map_html_path):
        st.write("Map loaded successfully!")
        # Read the HTML file content
        with open(map_html_path, 'r', encoding='utf-8') as file:
            map_html = file.read()

        # Embed the HTML file content into the Streamlit app
        st.components.v1.html(map_html, height=600)
    else:
        st.error("Map HTML file not found. Please ensure that the scripts ran correctly.")
