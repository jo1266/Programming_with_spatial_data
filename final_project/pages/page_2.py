import streamlit as st
import pandas as pd
import geopandas as gpd
import pydeck as pdk
import folium
from streamlit_folium import st_folium

st.title("🗺 Fire Map View")

# --- Check if data exists ---
if "df" not in st.session_state:
    st.warning("No data available. Please fetch data on the main page first.")
    st.stop()

df = st.session_state["df"]

# --- Validate data ---
if df.empty:
    st.warning("Dataset is empty.")
    st.stop()

if "latitude" not in df.columns or "longitude" not in df.columns:
    st.error("Missing latitude/longitude columns.")
    st.stop()

# --- Display map ---
st.subheader("🔥 Fire Detections")

map_df = df.rename(columns={"latitude": "lat", "longitude": "lon"})

st.map(map_df)

# --- Create datetime ---

# --- Ensure acq_date is string ---
df["acq_date"] = df["acq_date"].astype(str)

# --- Ensure acq_time is zero-padded string ---
df["acq_time"] = df["acq_time"].astype(str).str.zfill(4)

df["acq_datetime"] = pd.to_datetime(
    df["acq_date"] + " " + df["acq_time"],
    format="%Y-%m-%d %H%M",
    errors="coerce"
)

# --- Convert to GeoDataFrame ---
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.longitude, df.latitude),
    crs="EPSG:4326"
)

# --- time reference ---
now = pd.Timestamp.now()

# --- categories ---
df1 = df[df["acq_datetime"] >= (now - pd.Timedelta(hours=1))].copy()
df2 = df[(df["acq_datetime"] >= (now - pd.Timedelta(hours=4))) &
         (df["acq_datetime"] < (now - pd.Timedelta(hours=1)))].copy()
df3 = df[(df["acq_datetime"] >= (now - pd.Timedelta(hours=12))) &
         (df["acq_datetime"] < (now - pd.Timedelta(hours=4)))].copy()
df4 = df[df["acq_datetime"] < (now - pd.Timedelta(hours=12))].copy()

# --- add category labels ---
df1["category"] = "≤1h"
df2["category"] = "1–4h"
df3["category"] = "4–12h"
df4["category"] = ">12h"

# --- merge ---
df_all = pd.concat([df1, df2, df3, df4])

# --- rename for map ---
df_all = df_all.rename(columns={"latitude": "lat", "longitude": "lon"})

# --- color encoding ---
color_map = {
    "≤1h": [139, 0, 0],       # dark red
    "1–4h": [255, 0, 0],      # red
    "4–12h": [255, 165, 0],   # orange
    ">12h": [255, 255, 0],    # yellow
}

df_all["color"] = df_all["category"].map(color_map)

st.subheader("Fires timing categories")

# --- interactive map ---

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_all,
    get_position='[lon, lat]',
    get_fill_color='color',
    radius_units="pixels",
    get_radius=5,
    pickable=True
)

view_state = pdk.ViewState(
    latitude=df_all["lat"].mean(),
    longitude=df_all["lon"].mean(),
    zoom=5
)

deck_1 = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{category}"}
)

st.pydeck_chart(deck_1)


st.subheader("Multi layer map")
# --- 🔥 Topographic terrain map ---

# --- center map ---
center_lat = df["latitude"].mean()
center_lon = df["longitude"].mean()

tile = st.selectbox("Select map tile",
            ("OpenTopoMap",   # best topo
            "Stamen Terrain",     # terrain style
            "CartoDB positron",   # clean minimal
            "Esri.WorldImagery") #sattelite
)

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=6,
    tiles=tile
    )

# --- add markers ---
for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=3,
        color="red",
        fill=True,
        fill_opacity=0.7
    ).add_to(m)

st_folium(m, width=700, height=500)
