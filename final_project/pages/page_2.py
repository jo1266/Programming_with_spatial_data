import streamlit as st
import pandas as pd
import geopandas as gpd
import pydeck as pdk
import folium
from streamlit_folium import st_folium

st.title("🗺 Fire Map View")

# Existing data check
if "df" not in st.session_state:
    st.warning("No data available. Please fetch data on the main page first.")
    st.stop()

df = st.session_state["df"]

# Data validation
if df.empty:
    st.warning("Dataset is empty.")
    st.stop()

# Verifying coordinates availability
if "latitude" not in df.columns or "longitude" not in df.columns:
    st.error("Missing latitude/longitude columns.")
    st.stop()

# Display map
st.subheader(" Current wildfires visualization")

map_df = df.rename(columns={"latitude": "lat", "longitude": "lon"})

st.map(map_df)

# Setting date as string type
df["acq_date"] = df["acq_date"].astype(str)

# Ensure acq_time is zero-padded string
df["acq_time"] = df["acq_time"].astype(str).str.zfill(4)

# Setting the right date format
df["acq_datetime"] = pd.to_datetime(
    df["acq_date"] + " " + df["acq_time"],
    format="%Y-%m-%d %H%M",
    errors="coerce"
)

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.longitude, df.latitude),
    crs="EPSG:4326"
)

# Setting time reference
now = pd.Timestamp.now()

# Time categories
df1 = df[df["acq_datetime"] >= (now - pd.Timedelta(hours=1))].copy()
df2 = df[(df["acq_datetime"] >= (now - pd.Timedelta(hours=4))) &
         (df["acq_datetime"] < (now - pd.Timedelta(hours=1)))].copy()
df3 = df[(df["acq_datetime"] >= (now - pd.Timedelta(hours=12))) &
         (df["acq_datetime"] < (now - pd.Timedelta(hours=4)))].copy()
df4 = df[df["acq_datetime"] < (now - pd.Timedelta(hours=12))].copy()

# Add category labels
df1["category"] = "≤1h"
df2["category"] = "1–4h"
df3["category"] = "4–12h"
df4["category"] = ">12h"

# Merge categories
df_all = pd.concat([df1, df2, df3, df4])

# Variable renaming for map creation
df_all = df_all.rename(columns={"latitude": "lat", "longitude": "lon"})

# Categories color encoding
color_map = {
    "≤1h": [139, 0, 0],       # dark red
    "1–4h": [255, 0, 0],      # red
    "4–12h": [255, 165, 0],   # orange
    ">12h": [255, 255, 0],    # yellow
}

df_all["color"] = df_all["category"].map(color_map)

st.subheader("Wirldfires starting time categories")

st.info("Hover over points to get information")

# Implementing interactive map

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_all,
    get_position='[lon, lat]',
    get_fill_color='color',
    radius_units="pixels",
    get_radius=5,
    pickable=True
)

# Focus on previously selected country
view_state = pdk.ViewState(
    latitude=df_all["lat"].mean(),
    longitude=df_all["lon"].mean(),
    zoom=5
)

# Getting time categories while hoovering above points
deck_1 = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{category}"}
)

# Map visualization
st.pydeck_chart(deck_1)


st.subheader("Multi layer map")

# Center map definition
center_lat = df["latitude"].mean()
center_lon = df["longitude"].mean()

available_layers = {
    "topographic": "OpenTopoMap",
    "satellite": "Esri.WorldImagery",
    "base map": "CartoDB positron",
    "terrain": "Stamen Terrain"
}

selection = st.selectbox(
    label="Select the desired map layer",
    options=available_layers.keys()
)

tile = available_layers[selection]


# Map visualization
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=6,
    tiles=tile
    )

# Add markers
for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=3,
        color="red",
        fill=True,
        fill_opacity=0.7
    ).add_to(m)

st_folium(m, width=700, height=500)
