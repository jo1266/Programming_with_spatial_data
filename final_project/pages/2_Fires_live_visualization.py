import streamlit as st
import pandas as pd
import pydeck as pdk
import folium
from streamlit_folium import st_folium

st.title("Fires Visualization")

# Existing data check
if "df" not in st.session_state:
    st.warning("No data available. Please fetch data on page 1 first.")
    st.stop()
else:
    df = st.session_state["df"].copy()

# Data validation
if df.empty:
    st.warning("Dataset is empty.")
    st.stop()

# Verifying coordinates availability
if "latitude" not in df.columns or "longitude" not in df.columns:
    st.error("Missing latitude/longitude columns.")
    st.stop()

# Making sure lat and long are integers
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

df_map1 = df.dropna(subset=["latitude", "longitude"]).copy()

# Display map
st.subheader("Current wildfires visualization")

map_df = df_map1.rename(columns={"latitude": "lat", "longitude": "lon"})

st.map(map_df)

df_time = df_map1.copy()

# Date + time check
if "acq_date" not in df_time.columns or "acq_time" not in df_time.columns:
    st.warning("Missing acquisition date or time, so time categories cannot be created.")
    st.stop()

# Setting the right date format
date_str = df_time["acq_date"].astype(str).str[:10]

# Setting the right time format
time_str = (
        df_time["acq_time"]
        .astype(str)
        .str.replace(".0", "", regex=False)
        .str.extract(r"(\d+)", expand=False)
        .fillna("")
        .str.zfill(4)
    )

# Handling different time formats
valid_time = (
    time_str.str.len().eq(4) &
    time_str.str[:2].astype(int).between(0, 23) &
    time_str.str[2:].astype(int).between(0, 59)
)

# Clear dataframe separation
df_time = df_time[valid_time].copy()
time_str = time_str[valid_time]

# Setting the right date format
df_time["acq_datetime_new"] = pd.to_datetime(
    date_str + " " + time_str,
    format="%Y-%m-%d %H%M",
    errors="coerce"
)

# Keeping only relevant columns
df_new = df_time.dropna(
    subset=["latitude", "longitude", "acq_datetime_new"]
).copy()

# Error handling
if df_new.empty:
    st.warning("No valid fire detections after parsing coordinates and acquisition time.")
    st.stop()

# Setting time reference
dt_max = df_new["acq_datetime_new"].max()

# Time categories
df1 = df_new[df_new["acq_datetime_new"] >= (dt_max - pd.Timedelta(hours=1))].copy()

df2 = df_new[
    (df_new["acq_datetime_new"] >= (dt_max - pd.Timedelta(hours=4))) &
    (df_new["acq_datetime_new"] < (dt_max - pd.Timedelta(hours=1)))
].copy()

df3 = df_new[
    (df_new["acq_datetime_new"] >= (dt_max - pd.Timedelta(hours=12))) &
    (df_new["acq_datetime_new"] < (dt_max - pd.Timedelta(hours=4)))
    ].copy()

df4 = df_new[df_new["acq_datetime_new"] < (dt_max - pd.Timedelta(hours=12))].copy()

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

# Folium map creation
st.subheader("Multi layer map")

# Center map definition
center_lat = df_map1["latitude"].mean()
center_lon = df_map1["longitude"].mean()

# Layers selection options
available_layers = {
    "base map": "CartoDB positron",
    "topographic": "OpenTopoMap",
    "satellite": "Esri.WorldImagery"
}

# Actual layer selection
selection = st.selectbox(
    label="Select the desired map layer",
    options=available_layers.keys()
)

st.info("Click on points to get more information")

# Selected layer definition
tile = available_layers[selection]

# Map visualization
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=6,
    tiles=tile
    )

# Function to add time categories markers + metadata
def add_category_markers(data, color, name):

    feature_group = folium.FeatureGroup(name=name)

    for _, row in data.iterrows():

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=4,

            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.75,

            popup=f"""
            <b>Detection time:</b> {row['acq_datetime_new']}<br>
            <b>Brightness:</b> {row.get('brightness', 'N/A')}<br>
            <b>Confidence:</b> {row.get('confidence', 'N/A')}
            """
        ).add_to(feature_group)

    feature_group.add_to(m)


# Add already-defined time categories

if not df1.empty:
    add_category_markers(df1, "darkred", "Fires category ≤1 [h]")

if not df2.empty:
    add_category_markers(df2, "red", "Fires category 1-4 [h]")

if not df3.empty:
    add_category_markers(df3, "orange", "Fires category 4-12 [h]")

if not df4.empty:
    add_category_markers(df4, "yellow", "Fires category >12 [h]")


# Layer + fire categories control
folium.LayerControl(collapsed=True).add_to(m)


# Add legend

legend_html = """
<div style="
position: fixed;
bottom: 50px;
left: 10px;
width: 180px;
z-index:9999;
background-color:white;
padding:10px;
border:2px solid grey;
border-radius:8px;
font-size:14px;
color: black;
">

<b>Fire started:</b><br>

<i style="background:darkred;
width:12px;
height:12px;
display:inline-block;
border-radius:50%;"></i>
≤1 hour ago<br>

<i style="background:red;
width:12px;
height:12px;
display:inline-block;
border-radius:50%;"></i>
1-4 hours ago<br>

<i style="background:orange;
width:12px;
height:12px;
display:inline-block;
border-radius:50%;"></i>
4-12 hours ago<br>

<i style="background:yellow;
width:12px;
height:12px;
display:inline-block;
border-radius:50%;
border:1px solid black;"></i>
>12 hours ago

</div>
"""
# Show folium map
m.get_root().html.add_child(folium.Element(legend_html))

st_folium(m, width=700, height=500)