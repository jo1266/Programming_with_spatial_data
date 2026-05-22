import streamlit as st
import pandas as pd
import geopandas as gpd
import pydeck as pdk
import json
import requests

st.title("FIRMS Country Explorer")

# Load base map
@st.cache_data
def load_world():
    url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
    return gpd.read_file(url)

# Define europe
world = load_world()
europe = world[world["CONTINENT"] == "Europe"]

# Convert the GeoDataFrame into a proper GeoJSON dictonary
europe_json = json.loads(europe.to_json())

# Set the clickable map features
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

# Invalidation function to handle changes in dataset and timeframe selection
def invalidate_data():
    st.session_state.pop("df", None)

# Initialize state once
if "selected_country" not in st.session_state:
    st.session_state["selected_country"] = None

# Saving selection within an object type
if event is not None:
    selection = event.get("selection", {})
    objects = selection.get("objects", {}).get("countries", [])

    if objects:
        name = objects[0]["properties"]["NAME"]
        previous_country = st.session_state.get("selected_country")

        if name != previous_country:
            st.session_state["selected_country"] = name
            invalidate_data()

# Keeping selection active to re-use it later
selected_country = st.session_state["selected_country"]

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

    # Keeping country geometry bounds active
    st.session_state["country_bounds"] = {
        "minx": minx,
        "miny": miny,
        "maxx": maxx,
        "maxy": maxy
    }

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
    current_transactions = status_data.get("current_transactions", 0)
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
        st.error("Failed to get transactions count")

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
    end_count = get_transaction_count()
    st.success(f"Used transactions: {end_count - start_count}")

# Validating session state data
if "df_avail" in st.session_state:
    df_avail = st.session_state["df_avail"]
    st.dataframe(df_avail)

    if "selected_dataset" not in st.session_state:
        st.session_state["selected_dataset"] = "MODIS_NRT"
    
    selected_dataset = st.selectbox(
        "Select a dataset",
        df_avail["data_id"].unique(),
        #key="selected_dataset",
        on_change=invalidate_data
    )

    st.session_state["selected_dataset"] = selected_dataset

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

    else:
        st.info("Select a dataset")

else:
    st.info("Click 'Load Available Datasets' ")
    st.stop()

# Selection of timeframe
st.info("Drag the cursor to set the desired timeframe")

# Initialization of session state
if "days" not in st.session_state:
    st.session_state["days"] = 1

days = st.slider("Desired timeframe (days back from now)",
    min_value=1,
    max_value=10,
    step=1,
    #key="days",
    on_change=invalidate_data
)

if days:
    st.success(f"Selected timeframe: {days} day(s)")

# Keeping selection active
st.session_state["days"] = days

# Data source
url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{API_KEY}/{selected_dataset}/{minx},{miny},{maxx},{maxy}/{days}"

# FIRMS data fetching 
if selected_country and st.button("Fetch FIRMS Data"):
    try:
        st.subheader("Live Wildfires Data")
        start_count = get_transaction_count()
        df = pd.read_csv(url)
        st.session_state["df"] = df
        end_count = get_transaction_count()
        st.success(f"Used {end_count - start_count} transactions")
    except Exception as e:
        st.warning("Failed to fetch data")
        st.error("error:", e)

# Displaying the fetched dataframe
if "df" in st.session_state:
    df = st.session_state["df"]
    days = st.session_state["days"]
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

else:
    st.info("Click 'Fetch FIRMS data' ")