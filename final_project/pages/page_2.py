import streamlit as st
import pandas as pd
import geopandas as gpd
import pydeck as pdk
import folium
from streamlit_folium import st_folium

st.title("Fires Visualization")

# Existing data check
if "df" not in st.session_state:
    st.warning("No data available. Please fetch data on the main page first.")
    st.stop()
else:
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

st.info("Click on points to get more information")

tile = available_layers[selection]


# Map visualization
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=6,
    tiles=tile
    )


# ---------------------------------------------------
# Helper function to add category markers
# ---------------------------------------------------
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
            <b>Detection time:</b> {row['acq_datetime']}<br>
            <b>Brightness:</b> {row.get('brightness', 'N/A')}<br>
            <b>Confidence:</b> {row.get('confidence', 'N/A')}
            """
        ).add_to(feature_group)

    feature_group.add_to(m)

# ---------------------------------------------------
# Add already-defined time categories
# ---------------------------------------------------
if not df1.empty:
    add_category_markers(df1, "darkred", "Fires category ≤1 [h]")

if not df2.empty:
    add_category_markers(df2, "red", "Fires category 1-4 [h]")

if not df3.empty:
    add_category_markers(df3, "orange", "Fires category 4-12 [h]")

if not df4.empty:
    add_category_markers(df4, "yellow", "Fires category >12 [h]")

# ---------------------------------------------------
# Layer control
# ---------------------------------------------------
folium.LayerControl(collapsed=True).add_to(m)

# ---------------------------------------------------
# Add legend
# ---------------------------------------------------
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

m.get_root().html.add_child(folium.Element(legend_html))

st_folium(m, width=700, height=500)