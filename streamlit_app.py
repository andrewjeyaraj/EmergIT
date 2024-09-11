import streamlit as st
import os
import subprocess
import sys

# Get the current directory (where the Streamlit script is located)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the path to the final_page_renderer_production.py script and HTML file
final_renderer_path = os.path.join(current_dir, 'final_page_renderer_production.py')
map_html_path = os.path.join(current_dir, 'hospital_map_with_nearest_hospital_panel.html')

# Function to execute the final_page_renderer_production script without printing output
def run_script_silently(script_path):
    if os.path.exists(script_path):
        try:
            # Run the script without printing output to the Streamlit app
            result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
            if result.returncode == 0:
                st.success("Map generation completed successfully!")
            else:
                st.error(f"Error in {script_path}: {result.stderr}")
        except Exception as e:
            st.error(f"Failed to run {script_path}: {str(e)}")
    else:
        st.error(f"Script not found: {script_path}")

# Streamlit app starts here
st.title('Hospital Map Loader')

st.markdown("Welcome! Click the button below to generate and view the hospital map based on the latest data.")

# Button to trigger the loading and rendering of the map
if st.button('Load Map'):
    # Add an impression message to give feedback to the user
    st.write("Processing your request... Please wait while the map is being generated.")

    # Run final_page_renderer_production.py to generate the map silently
    run_script_silently(final_renderer_path)

    # Check if the HTML file exists and display the map
    if os.path.exists(map_html_path):
        st.write("Map loaded successfully!")
        # Read the HTML file content
        with open(map_html_path, 'r', encoding='utf-8') as file:
            map_html = file.read()

        # Embed the HTML file content into the Streamlit app with full width and larger height
        st.components.v1.html(f"""
            <div style="width: 100vw; height: 1200px;">
                {map_html}
            </div>
            """, height=1200)
    else:
        st.error("Map HTML file not found. Please ensure that the script ran correctly.")
