import streamlit as st
import pandas as pd
import geopandas as gpd
import pydeck as pdk
import geodatasets

st.title("🌍 FIRMS Country Explorer (Clickable Map)")

@st.cache_data
def load_world():
    path = geodatasets.get_path("naturalearth_lowres")
    return gpd.read_file(path)

world = load_world()
europe = world[world["continent"] == "Europe"]

europe_json = europe.__geo_interface__

layer = pdk.Layer(
    "GeoJsonLayer",
    europe_json,
    pickable=True,
    stroked=True,
    filled=True,
    get_fill_color=[180, 180, 180, 80],
    get_line_color=[0, 0, 0],
)

view_state = pdk.ViewState(
    latitude=50,
    longitude=10,
    zoom=3
)

r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{name}"}
)

event = st.pydeck_chart(r, on_select="rerun", selection_mode="single-object")

selected_country = None

if event and event.selection and event.selection.get("objects"):
    selected_country = event.selection["objects"][0]["name"]

st.write("Selected country:", selected_country)

if selected_country:
    country_geom = europe[europe["name"] == selected_country].geometry.values[0]
    minx, miny, maxx, maxy = country_geom.bounds

    st.write(f"BBox: {minx}, {miny}, {maxx}, {maxy}")

API_KEY = "b2f10217e4419203b51cddefcc979791"

dataset = st.selectbox(
    "Dataset",
    ["MODIS_NRT", "VIIRS_SNPP_NRT", "VIIRS_NOAA21_NRT"]
)

days = st.slider("Days back", 1, 10, 1)

if selected_country and st.button("Fetch FIRMS Data"):

    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{API_KEY}/{dataset}/{minx},{miny},{maxx},{maxy}/{days}"

    df = pd.read_csv(url)

    st.session_state["df_area"] = df

    st.subheader("🔥 Fire Data")
    st.dataframe(df)

    st.metric("Total detections", len(df))

    if not df.empty and "latitude" in df.columns:
        st.map(df.rename(columns={"latitude": "lat", "longitude": "lon"}))


"""
st.subheader("🌍 Select European Country")

country = st.selectbox("Choose a country", sorted(europe["name"].unique()))

country_geom = europe[europe["name"] == country].geometry.values[0]

minx, miny, maxx, maxy = country_geom.bounds

st.write(f"Selected bounding box: {minx:.2f}, {miny:.2f}, {maxx:.2f}, {maxy:.2f}")

west, south, east, north = minx, miny, maxx, maxy

days = st.slider("Days back", 1, 10, 1)

dataset = st.selectbox(
    "Dataset",
    ["MODIS_NRT", "VIIRS_SNPP_NRT", "VIIRS_NOAA21_NRT"]
)

if st.button("Fetch Fire Data for Country"):

    area_url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{"b2f10217e4419203b51cddefcc979791"}/{dataset}/{west},{south},{east},{north}/{days}"

    start_count = get_transaction_count()

    try:
        df_area = pd.read_csv(area_url)
        end_count = get_transaction_count()

        st.success(f"Used {end_count - start_count} transactions")

        st.session_state["df_area"] = df_area

        st.dataframe(df_area)

        # --- MAP ---
        if not df_area.empty and "latitude" in df_area.columns:
            st.subheader("🗺 Fire Map")
            st.map(df_area.rename(columns={"latitude": "lat", "longitude": "lon"}))

        # --- STATS ---
        st.subheader("📊 Basic Statistics")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total detections", len(df_area))

        if "confidence" in df_area.columns:
            col2.metric("High confidence fires",
                        len(df_area[df_area["confidence"] == "h"]))
        else:
            col2.metric("High confidence fires", "N/A")

        if "acq_date" in df_area.columns:
            df_area["acq_date"] = pd.to_datetime(df_area["acq_date"])
            daily = df_area.groupby("acq_date").size()
            col3.line_chart(daily)
        else:
            col3.metric("Time trend", "N/A")

    except Exception as e:
        st.error("Error fetching data")
        st.text(str(e))
"""