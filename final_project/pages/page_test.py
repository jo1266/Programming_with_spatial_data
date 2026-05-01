import streamlit as st
import pandas as pd
import geopandas as gpd
import pydeck as pdk
import geodatasets
import json

st.title("FIRMS Country Explorer")

@st.cache_data
def load_world():
    url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
    return gpd.read_file(url)

world = load_world()
europe = world[world["CONTINENT"] == "Europe"]

# --- Transaction count ---
def get_transaction_count():
    try:
        data = get_api_status()
        return data["current_transactions"]
    except:
        return 0
    
tcount = get_transaction_count()
st.metric("Current Transactions", tcount)

# Convert GeoDataFrame → proper GeoJSON dict
europe_json = json.loads(europe.to_json())

layer = pdk.Layer(
    "GeoJsonLayer",
    data=europe_json,
    id="countries",  # IMPORTANT
    pickable=True,
    auto_highlight=True,
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

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{NAME}"}
)

event = st.pydeck_chart(
    deck,
    use_container_width=True,
    on_select="rerun"
)

selected_country = None

#st.write("EVENT:", event)

#st.write("DEBUG selection object:", objects)
#st.write(objects[0].keys())

if event is not None:
    selection = event.get("selection", {})
    objects = selection.get("objects", {}).get("countries", [])

    if objects:
        name = objects[0]["properties"]["NAME"]
        st.session_state["selected_country"] = name

selected_country = st.session_state.get("selected_country")

if selected_country:
    st.success(f"Selected country: {selected_country}")
else:
    st.info("Click on a country")

if selected_country:
    country_geom = europe[europe["NAME"] == selected_country].geometry.values[0]
    minx, miny, maxx, maxy = country_geom.bounds

    st.write(f"BBox: {minx}, {miny}, {maxx}, {maxy}")


API_KEY = "b2f10217e4419203b51cddefcc979791"

# --- Data availability ---
st.subheader("Available Datasets")

da_url = f"https://firms.modaps.eosdis.nasa.gov/api/data_availability/csv/{API_KEY}/all"

@st.cache_data
def load_availability():
    return pd.read_csv(da_url)

if st.button("Load Available Datasets"):
    df_avail = load_availability()
    st.dataframe(df_avail)

st.subheader("Dataset selection")
dataset = st.selectbox(
    "dataset",
    ["MODIS_NRT", "VIIRS_SNPP_NRT", "VIIRS_NOAA21_NRT"]
)

days = st.slider("Days back", 1, 10, 1)

if selected_country and st.button("Fetch FIRMS Data"):

    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{API_KEY}/{dataset}/{minx},{miny},{maxx},{maxy}/{days}"
    
    start_count = get_transaction_count()

    try:
        df = pd.read_csv(url)

        st.session_state["df"] = df
        # --- selected country ---
        st.session_state["selected_country"] = selected_country

        # --- country geometry bounds ---
        st.session_state["country_bounds"] = {
        "minx": minx,
        "miny": miny,
        "maxx": maxx,
        "maxy": maxy
        }

        end_count = get_transaction_count()
        st.success(f"Used {end_count - start_count} transactions")

        st.subheader("🔥 Fire Data")
        st.dataframe(df)

        st.metric("Total detections", len(df))

        # --- STATS ---
        st.subheader("📊 Basic Statistics")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total detections", len(df))

        if "confidence" in df.columns:
            col2.metric("High confidence fires",
                        len(df[df["confidence"] == "h"]))
        else:
            col2.metric("High confidence fires", "N/A")

        if "acq_date" in df.columns:
            df["acq_date"] = pd.to_datetime(df["acq_date"])
            daily = df.groupby("acq_date").size()
            col3.line_chart(daily)
        else:
            col3.metric("Time trend", "N/A")

    except Exception as e:
        st.error("Error fetching data")
        st.text(str(e))



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