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

@st.cache_data
def load_world():
    url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
    return gpd.read_file(url)

world = load_world()
europe = world[world["CONTINENT"] == "Europe"]

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

    st.write(f"Geographical extent (West, South, Est, North): {minx}, {miny}, {maxx}, {maxy}")

API_KEY = "b2f10217e4419203b51cddefcc979791"
api_url = f"https://firms.modaps.eosdis.nasa.gov/mapserver/mapkey_status/?MAP_KEY={API_KEY}"

#@st.cache_data
def get_api_status():
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    return None

status_data = get_api_status()

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

# --- Transaction count ---
def get_transaction_count():
    try:
        data = get_api_status()
        return data["current_transactions"]
    except:
        return 0

# --- Data availability ---
st.subheader("Available Datasets")

da_url = f"https://firms.modaps.eosdis.nasa.gov/api/data_availability/csv/{API_KEY}/all"

#@st.cache_data
def load_availability():
    return pd.read_csv(da_url)

if st.button("Load Available Datasets"):
    start_count = get_transaction_count()
    df_avail = load_availability()
    st.session_state["df_avail"] = df_avail
    st.dataframe(df_avail)
    end_count = get_transaction_count()
    st.success(f"Used transactions: {end_count - start_count}")

if "df_avail" in st.session_state:
    df_avail = st.session_state["df_avail"]

    st.dataframe(df_avail)

    selected_dataset = st.selectbox(
        "🔎 Select dataset",
        df_avail["data_id"].unique()
    )
    if selected_dataset:
        st.success(f"Selected dataset: {selected_dataset}")

        dataset_info = df_avail[df_avail["data_id"] == selected_dataset].iloc[0]

        st.subheader(f"📦 {selected_dataset}")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("**Sensor:**", dataset_info.get("sensor", "N/A"))
        col2.metric("**Satellite:**", dataset_info.get("satellite", "N/A"))
        col3.metric("**Resolution:**", dataset_info.get("resolution", "N/A"))
        col4.metric("**Coverage:**", dataset_info.get("coverage", "N/A"))

        # Optional: full row
        with st.expander("🔍 Full metadata"):
            st.write(dataset_info)

    ROOT = Path(__file__).resolve().parent
    DOC = ROOT / "final_project" / "LCA_structure.png"

    else:
        st.info("Select a dataset")

else:
    st.info("Click 'Load Available Datasets' first")
    st.stop()

days = st.slider("Days back", 1, 10, 1)

if selected_country and st.button("Fetch FIRMS Data"):

    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{API_KEY}/{selected_dataset}/{minx},{miny},{maxx},{maxy}/{days}"
    
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

        # --- STATS ---
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

