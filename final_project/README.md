# Project title

Live statistics and visualization of wildfires across Europe

## Project description

Streamlit interface that allow users to: fetch live wildfires data from the FIRMS for a specific EU country, get information about basic statistical facts, visualize it within different map sorts, use a live windy map potentially useful to understand how these fires will evolve, and grasp potential consequences of these fires by generating an air quality map.

## Data sources

* Wildfires data: https://firms.modaps.eosdis.nasa.gov/api/area/
* Primary code structure comes from: https://firms.modaps.eosdis.nasa.gov/content/academy/data_api/firms_api_use.html
* Initial ideas of visualization taken from: https://firms.modaps.eosdis.nasa.gov/content/academy/data_visualization/firms_visualization.html
* Air quality data is from: https://open-meteo.com/en/docs/air-quality-api

## Setup instruction

* The file "requirements.txt" indicates which libraries are used within this project's code
* These specific libraries are the following: streamlit, pandas, requests, geopandas, pydeck, folium,streamlit_folium, numpy 

## Execution order

* Download the "final_project" folder locally on your machine
* Download the required libraries
* In your terminal, go to the folder "final_project"
* From there, enter the following command: streamlit run introduction.py
* Or... Simply click on this link to access the deployed app: https://wildfires-across-europe.streamlit.app/
