import streamlit as st
import pandas as pd
import requests

st.title("NASA FIRMS Fire Data Explorer")

# --- API status ---
API_KEY = "b2f10217e4419203b51cddefcc979791"

api_url = f"https://firms.modaps.eosdis.nasa.gov/mapserver/mapkey_status/?MAP_KEY={API_KEY}"

@st.cache_data
def get_api_status():
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    return None

status_data = get_api_status()

if status_data:
    df_status = pd.Series(status_data)
    st.subheader("API Status")
    st.json(status_data)
else:
    st.error("Failed to fetch API status")

# --- Transaction count ---
def get_transaction_count():
    try:
        data = get_api_status()
        return data["current_transactions"]
    except:
        return 0

tcount = get_transaction_count()
st.metric("Current Transactions", tcount)

# --- Data availability ---
st.subheader("Available Datasets")

da_url = f"https://firms.modaps.eosdis.nasa.gov/api/data_availability/csv/{API_KEY}/all"

@st.cache_data
def load_availability():
    return pd.read_csv(da_url)

if st.button("Load Available Datasets"):
    df_avail = load_availability()
    st.dataframe(df_avail)

# --- Area selection ---
st.subheader("Fetch Fire Data by Area")

col1, col2 = st.columns(2)

with col1:
    west = st.number_input("West (lon)", value=-10)
    south = st.number_input("South (lat)", value=35)

with col2:
    east = st.number_input("East (lon)", value=15)
    north = st.number_input("North (lat)", value=60)

days = st.slider("Days back", 1, 10, 1)

dataset = st.selectbox(
    "Dataset",
    ["MODIS_NRT", "VIIRS_SNPP_NRT", "VIIRS_NOAA21_NRT"]
)

# --- Fetch area data ---
if st.button("Fetch Fire Data"):
    area_url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{API_KEY}/{dataset}/{west},{south},{east},{north}/{days}"

    start_count = get_transaction_count()

    try:
        df_area = pd.read_csv(area_url)
        end_count = get_transaction_count()

        st.success(f"Used {end_count - start_count} transactions")

        st.dataframe(df_area)

        # Optional: map visualization
        if "latitude" in df_area.columns and "longitude" in df_area.columns:
            st.subheader("Map View")
            st.map(df_area.rename(columns={"latitude": "lat", "longitude": "lon"}))

    except Exception as e:
        st.error("Error fetching data")
        st.text(str(e))

    st.session_state["df_area"] = df_area