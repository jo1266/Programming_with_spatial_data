# Project title

Live statistics and visualization of wildfires across Europe

## Project description

Streamlit interface that allow users to fetch live wildfires data from the FIRMS for a specific EU country, get information about basic statistical facts, visualize it within different map sorts, and provide a windy layout in order to grasp potential consequences of these fires. 

## Data sources
* Wildfires data: https://firms.modaps.eosdis.nasa.gov/api/area/
* Primary code structure comes from: https://firms.modaps.eosdis.nasa.gov/content/academy/data_api/firms_api_use.html
* Initial ideas of visualization taken from: https://firms.modaps.eosdis.nasa.gov/content/academy/data_visualization/firms_visualization.html
*

## Setup instruction
* download the global geo packages from the channel "conda forge"
* download these specific libraries via pip: cmcrameri, pydeck, streamlit, streamlit-folium, 

## Execution order
* Download the "final_project" folder locally on your machine
* Download the required packages and dependencies
* Simply enter the following command in your terminal: streamlit run content.py
