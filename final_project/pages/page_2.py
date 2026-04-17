import streamlit as st
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily as cx
from geodatasets import get_path

st.title("🔥 Fire Map Visualization")

# --- Load data from first page ---
if "df_area" not in st.session_state:
    st.error("No data found. Please fetch data on the main page first.")
    st.stop()

df_area = st.session_state["df_area"]

# --- Load world basemap ---
@st.cache_data
def load_world():
    path = get_path("naturalearth.land")
    return geopandas.read_file(path)

world = load_world()
world = world.to_crs("EPSG:4326")

# --- Convert to GeoDataFrame ---
gdf = geopandas.GeoDataFrame(
    df_area,
    geometry=geopandas.points_from_xy(df_area.longitude, df_area.latitude),
    crs="EPSG:4326"
)

st.subheader("Global Fire Map")

fig, ax = plt.subplots()
world.plot(ax=ax, color="lightgrey", edgecolor="black")
gdf.plot(ax=ax, color="red", markersize=0.5)

st.pyplot(fig)

# --- Australia subset ---
st.subheader("Australia Focus")

df_australia = df_area[
    (df_area['longitude'] >= 112) &
    (df_area['latitude'] >= -44) &
    (df_area['longitude'] <= 154) &
    (df_area['latitude'] <= -10)
].copy()

gdf_aus = geopandas.GeoDataFrame(
    df_australia,
    geometry=geopandas.points_from_xy(df_australia.longitude, df_australia.latitude),
    crs="EPSG:4326"
)

extent = [112, -44, 154, -10]

fig2, ax2 = plt.subplots(figsize=(8, 8))
world.plot(ax=ax2, color="grey", edgecolor="black")

ax2.set_xlim([extent[0], extent[2]])
ax2.set_ylim([extent[1], extent[3]])
ax2.set_title("Australia Wildfires")

gdf_aus.plot(ax=ax2, color="red", markersize=1)

st.pyplot(fig2)

# --- Time-based visualization ---
st.subheader("⏱ Time Since Detection")

df_australia['acq_datetime'] = pd.to_datetime(
    df_australia['acq_date'] + ' ' +
    df_australia['acq_time'].astype(str).str.zfill(4),
    format='%Y-%m-%d %H%M'
)

gdf = geopandas.GeoDataFrame(
    df_australia,
    geometry=geopandas.points_from_xy(df_australia.longitude, df_australia.latitude),
    crs="EPSG:4326"
)

dt_max = pd.Timestamp.now()

gdf1 = gdf[gdf['acq_datetime'] >= (dt_max - pd.Timedelta(hours=1))]
gdf2 = gdf[(gdf['acq_datetime'] >= (dt_max - pd.Timedelta(hours=4))) &
           (gdf['acq_datetime'] < (dt_max - pd.Timedelta(hours=1)))]
gdf3 = gdf[(gdf['acq_datetime'] >= (dt_max - pd.Timedelta(hours=12))) &
           (gdf['acq_datetime'] < (dt_max - pd.Timedelta(hours=4)))]
gdf4 = gdf[gdf['acq_datetime'] < (dt_max - pd.Timedelta(hours=12))]

st.subheader("Counts")

col1, col2, col3, col4 = st.columns(4)

col1.metric("≤1h", len(gdf1) if 'gdf1' in locals() else 0)
col2.metric("1–4h", len(gdf2) if 'gdf2' in locals() else 0)
col3.metric("4–12h", len(gdf3) if 'gdf3' in locals() else 0)
col4.metric(">12h", len(gdf4) if 'gdf4' in locals() else 0)

# --- Plot time categories ---
fig3, ax3 = plt.subplots(figsize=(8, 8))
world.plot(ax=ax3, color="grey", edgecolor="black")

ax3.set_xlim([extent[0], extent[2]])
ax3.set_ylim([extent[1], extent[3]])
ax3.set_title("Time Since Detection (Australia)")


if not gdf4.empty:
    gdf4.plot(ax=ax3, color="yellow", markersize=1)
if not gdf3.empty:
    gdf3.plot(ax=ax3, color="orange", markersize=1)
if not gdf2.empty:
    gdf2.plot(ax=ax3, color="red", markersize=1)
if not gdf1.empty:
    gdf1.plot(ax=ax3, color="darkred", markersize=1)


st.pyplot(fig3)

# --- Basemap version ---
st.subheader("🗺 With Basemap")

fig4, ax4 = plt.subplots(figsize=(8, 8))

ax4.set_xlim([extent[0], extent[2]])
ax4.set_ylim([extent[1], extent[3]])
ax4.set_axis_off()
ax4.set_title("Australia Wildfires (Basemap)")

if len(gdf4) > 0:
    gdf4.plot(ax=ax4, color="yellow", markersize=1)
if len(gdf3) > 0:
    gdf3.plot(ax=ax4, color="orange", markersize=1)
if len(gdf2) > 0:
    gdf2.plot(ax=ax4, color="red", markersize=1)
if len(gdf1) > 0:
    gdf1.plot(ax=ax4, color="darkred", markersize=1)

cx.add_basemap(ax4, crs=gdf.crs)

st.pyplot(fig4)