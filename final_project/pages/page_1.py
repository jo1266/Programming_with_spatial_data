import streamlit as st
import pandas as pd
import geopandas as gpd
import pydeck as pdk
import json
import requests
from pypdf import PdfReader
from openai import OpenAI
import os

st.title("FIRMS Country Explorer")

# Load base map
@st.cache_data
def load_world():
    url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
    return gpd.read_file(url)

# Define europe
world = load_world()
europe = world[world["CONTINENT"] == "Europe"]

# Convert GeoDataFrame → proper GeoJSON dict
europe_json = json.loads(europe.to_json())

layer = pdk.Layer(
    "GeoJsonLayer",
    data=europe_json,
    id="countries",
    pickable=True,
    auto_highlight=True,
    stroked=True,
    filled=True,
    get_fill_color=[180, 180, 180, 80],
    get_line_color=[0, 0, 0],
)

# Set PyDeck interface
view_state = pdk.ViewState(
    latitude=50,
    longitude=10,
    zoom=3
)

# Get country names by hoovering on the map
deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{NAME}"}
)

# Country selection function
event = st.pydeck_chart(
    deck,
    use_container_width=True,
    on_select="rerun"
)

# Variable definition
selected_country = None

# Saving selection within an object type
if event is not None:
    selection = event.get("selection", {})
    objects = selection.get("objects", {}).get("countries", [])

    if objects:
        name = objects[0]["properties"]["NAME"]
        st.session_state["selected_country"] = name

# Keeping selection active to re-use it later
selected_country = st.session_state.get("selected_country")

# Selection status tool
if selected_country:
    st.success(f"Selected country: {selected_country}")
else:
    st.info("Click on a country")

# Getting geographical extent of the selected country
if selected_country:
    country_geom = europe[europe["NAME"] == selected_country].geometry.values[0]
    minx, miny, maxx, maxy = country_geom.bounds

    st.write(f"Geographical extent (West, South, Est, North): {minx}, {miny}, {maxx}, {maxy}")

# API infos
API_KEY = "b2f10217e4419203b51cddefcc979791"
api_url = f"https://firms.modaps.eosdis.nasa.gov/mapserver/mapkey_status/?MAP_KEY={API_KEY}"

# API status function
#@st.cache_data
def get_api_status():
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    return None

status_data = get_api_status()

# Initial API status
if status_data:
    df_status = pd.Series(status_data)
    st.subheader("API Status")
    current_transactions = status_data.get("current_transaction", 0)
    transactions_limit = status_data.get("transaction_limit", 0)
    transaction_interval = status_data.get("transaction_interval", 0)
    col1, col2, col3 = st.columns(3)

    col1.metric("Current transactions", current_transactions)
    col2.metric("Transactions limit", transactions_limit)
    col3.metric("Transaction interval", transaction_interval)
else:
    st.error("Failed to fetch API status")

# Transaction count function
def get_transaction_count():
    try:
        data = get_api_status()
        return data["current_transactions"]
    except:
        return 0

# Getting datasets availability
st.subheader("Available Datasets")

da_url = f"https://firms.modaps.eosdis.nasa.gov/api/data_availability/csv/{API_KEY}/all"

# Function to fetch available datasets
#@st.cache_data
def load_availability():
    return pd.read_csv(da_url)

# Fetching available datasets and transaction count
if st.button("Load Available Datasets"):
    start_count = get_transaction_count()
    df_avail = load_availability()
    st.session_state["df_avail"] = df_avail
    st.dataframe(df_avail)
    end_count = get_transaction_count()
    st.success(f"Used transactions: {end_count - start_count}")

# Keeping selected dataset active
if "df_avail" in st.session_state:
    df_avail = st.session_state["df_avail"]

    st.dataframe(df_avail)

    selected_dataset = st.selectbox(
        "🔎 Select dataset",
        df_avail["data_id"].unique()
    )

    # Detailed description of each dataset
    DATASET_DESCRIPTIONS = {
    "MODIS_NRT": "Near real-time fire detection used for fast updates containing moderate detail.",
    "MODIS_SP": "Post-processed MODIS fire data with more accuracy than 'MODIS_NRT' but delayed availability.",

    "VIIRS_SNPP_NRT": "Near real-time fire detection that is reliable and widely used.",
    "VIIRS_SNPP_SP": "Post-processed data with improved accuracy and fewer false detections.",

    "VIIRS_NOAA20_NRT": "Near real-time fire detection with enhanced temporal coverage.",
    "VIIRS_NOAA20_SP": "Validated dataset from 'VIIRS_NOAA20_NRT' with higher reliability but delayed access.",

    "VIIRS_NOAA21_NRT": "More recent dataset compared to 'VIIRS_NOAA20_NRT' that improves revisit frequency and coverage.",

    "LANDSAT_NRT": "Very high-resolution fire detection that is highly detailed but with infrequent coverage.",
    "GOES_NRT": "Geostationary fire detection with excellent temporal tracking, but coarse resolution.",

    "BA_MODIS": "Burned area dataset that identifies areas already affected by fires.",
    "BA_VIIRS": "High-resolution burned area mapping for post-fire analysis."
    }

    # Metadata of each dataset
    DATASET_METADATA = {
    "MODIS_NRT": {
        "sensor": "MODIS",
        "satellite": "Terra & Aqua",
        "resolution": "~1 km",
        "coverage": "Global"
    },
    "MODIS_SP": {
        "sensor": "MODIS",
        "satellite": "Terra & Aqua",
        "resolution": "~1 km",
        "coverage": "Global"
    },

    "VIIRS_SNPP_NRT": {
        "sensor": "VIIRS",
        "satellite": "Suomi NPP",
        "resolution": "~375 m",
        "coverage": "Global"
    },
    "VIIRS_SNPP_SP": {
        "sensor": "VIIRS",
        "satellite": "Suomi NPP",
        "resolution": "~375 m",
        "coverage": "Global"
    },

    "VIIRS_NOAA20_NRT": {
        "sensor": "VIIRS",
        "satellite": "NOAA-20",
        "resolution": "~375 m",
        "coverage": "Global"
    },
    "VIIRS_NOAA20_SP": {
        "sensor": "VIIRS",
        "satellite": "NOAA-20",
        "resolution": "~375 m",
        "coverage": "Global"
    },

    "VIIRS_NOAA21_NRT": {
        "sensor": "VIIRS",
        "satellite": "NOAA-21",
        "resolution": "~375 m",
        "coverage": "Global"
    },

    "LANDSAT_NRT": {
        "sensor": "OLI/TIRS",
        "satellite": "Landsat 8/9",
        "resolution": "~30 m",
        "coverage": "Global (low revisit)"
    },

    "GOES_NRT": {
        "sensor": "ABI",
        "satellite": "GOES-East/West",
        "resolution": "~2 km",
        "coverage": "Americas"
    },

    "BA_MODIS": {
        "sensor": "MODIS",
        "satellite": "Terra & Aqua",
        "resolution": "~500 m",
        "coverage": "Global"
    },

    "BA_VIIRS": {
        "sensor": "VIIRS",
        "satellite": "SNPP / NOAA-20",
        "resolution": "~375 m",
        "coverage": "Global"
    }
    }
    
    # Getting datasets infos
    if selected_dataset:
        st.success(f"Selected dataset: {selected_dataset}")

        # --- Description ---
        description = DATASET_DESCRIPTIONS.get(
        selected_dataset,
        "No description available."
        )

        st.markdown("### General description")
        st.info(description)

        metadata = DATASET_METADATA.get(selected_dataset, {})

        st.markdown("### Dataset metadata")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("**Sensor:**", metadata.get("sensor", "N/A"), width="content")
        col2.metric("**Satellite:**", metadata.get("satellite", "N/A"), width="stretch")
        col3.metric("**Resolution:**", metadata.get("resolution", "N/A"), width="content")
        col4.metric("**Coverage:**", metadata.get("coverage", "N/A"), width="content")

        #ROOT = Path(__file__).resolve().parent
        #DOC = ROOT / "final_project" / "LCA_structure.png"

    else:
        st.info("Select a dataset")

else:
    st.info("Click 'Load Available Datasets' first")
    st.stop()

# Selection of timeframe
days = st.slider("Days back", 1, 10, 1)

# FIRMS data fetching 
if selected_country and st.button("Fetch FIRMS Data"):

    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{API_KEY}/{selected_dataset}/{minx},{miny},{maxx},{maxy}/{days}"
    
    start_count = get_transaction_count()

    try:
        df = pd.read_csv(url)

        st.session_state["df"] = df
        # Selected country
        st.session_state["selected_country"] = selected_country

        # Country geometry bounds
        st.session_state["country_bounds"] = {
        "minx": minx,
        "miny": miny,
        "maxx": maxx,
        "maxy": maxy
        }

        # Transaction count
        end_count = get_transaction_count()
        st.success(f"Used {end_count - start_count} transactions")

        st.subheader("🔥 Fire Data")
        st.dataframe(df)

        # Statistical description
        st.subheader("📊 Basic Statistics")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total detections", len(df))

        if "confidence" in df.columns:
            col2.metric("Average confidence",
                        round(df["confidence"].mean(), 2))
        else:
            col2.metric("Average confidence", "N/A")

        if "brightness" in df.columns:
            col3.metric("Average brightness",
                        round(df["brightness"].mean(), 2))
        else:
            col3.metric("Time trend", "N/A")

    except Exception as e:
        st.error("Error fetching data")
        st.text(str(e))

