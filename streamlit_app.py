import streamlit as st
import os
import subprocess
import sys

# Get the current directory (where the Streamlit script is located)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the path to the final_page_renderer_production.py script and HTML file
final_renderer_path = os.path.join(current_dir, 'final_page_renderer_production.py')
map_html_path = os.path.join(current_dir, 'hospital_map_with_nearest_hospital_panel.html')

# Function to execute the final_page_renderer_production script
def run_script(script_path):
    if os.path.exists(script_path):
        try:
            result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
            st.write(f"Running {script_path}...")
            st.write(result.stdout)  # Print the output of the script
            if result.stderr:
                st.error(f"Error in {script_path}: {result.stderr}")
        except Exception as e:
            st.error(f"Failed to run {script_path}: {str(e)}")
    else:
        st.error(f"Script not found: {script_path}")

# Streamlit app starts here
st.title('Hospital Map Loader')

# Button to trigger the loading and rendering of the map
if st.button('Load Map'):
    # Run final_page_renderer_production.py to generate the map
    run_script(final_renderer_path)

    # Check if the HTML file exists and display the map
    if os.path.exists(map_html_path):
        st.write("Map loaded successfully!")
        # Read the HTML file content
        with open(map_html_path, 'r', encoding='utf-8') as file:
            map_html = file.read()

        # Embed the HTML file content into the Streamlit app
        st.components.v1.html(map_html, height=800)  # Make the map larger (height adjusted to 800)
    else:
        st.error("Map HTML file not found. Please ensure that the script ran correctly.")
