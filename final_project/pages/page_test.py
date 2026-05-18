from pypdf import PdfReader
from openai import OpenAI
import os
import streamlit as st
from pathlib import Path
import requests
import pandas as pd
import geopandas as gpd
import pydeck as pdk

# Data availability check
if "selected_country" not in st.session_state:
    st.warning("Missing selected country.")
    st.stop()

if "country_bounds" not in st.session_state:
    st.warning("Country bounds not available.")
    st.stop()

# Data validation
minx = st.session_state["country_bounds"]["minx"]
miny = st.session_state["country_bounds"]["miny"]
maxx = st.session_state["country_bounds"]["maxx"]
maxy = st.session_state["country_bounds"]["maxy"]

# Initial calculations
center_lat = (miny + maxy) / 2
center_lon = (minx + maxx) / 2
lat_range = abs(maxy - miny)
lon_range = abs(maxx - minx)
max_range = max(lat_range, lon_range)

# Zooming settings
if max_range < 2:
    zoom = 8.5
elif max_range < 5:
    zoom = 7.5
elif max_range < 10:
    zoom = 6.5
elif max_range < 20:
    zoom = 5.5
else:
    zoom = 4.5

VARIABLES = {
    "PM2.5": "pm2_5",
    "PM10": "pm10",
    "Carbon Monoxide (CO)": "carbon_monoxide",
    "Nitrogen Dioxide (NO2)": "nitrogen_dioxide",
    "Ozone (O3)": "ozone",
    "Sulphur Dioxide (SO2)": "sulphur_dioxide",
    "Aerosol Optical Depth": "aerosol_optical_depth",
    "Dust": "dust",
    "UV Index": "uv_index"
}

selected_vars = st.multiselect(
    "Select air quality variables",
    list(VARIABLES.keys()),
    default=["PM2.5", "PM10"]
)

var_params = ",".join([VARIABLES[v] for v in selected_vars])

# -----------------------------
# API request
# -----------------------------
@st.cache_data
def fetch_air_quality(minx, miny, maxx, maxy, variables):
    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={ (miny + maxy) / 2 }"
        f"&longitude={ (minx + maxx) / 2 }"
        f"&hourly={variables}"
        "&timezone=auto"
    )

    response = requests.get(url)
    response.raise_for_status()
    return response.json()

if st.button("Fetch Air Quality Data"):

    try:
        data = fetch_air_quality(minx, miny, maxx, maxy, var_params)

        # -----------------------------
        # Convert to dataframe
        # -----------------------------
        df = pd.DataFrame(data["hourly"])
        st.session_state["air_quality_df"] = df

        st.success("Data loaded successfully")

        st.subheader("📊 Air Quality Data")
        st.dataframe(df)

        # -----------------------------
        # Simple plots
        # -----------------------------
        if "pm2_5" in df.columns:
            st.line_chart(df.set_index("time")["pm2_5"])

        if "pm10" in df.columns:
            st.line_chart(df.set_index("time")["pm10"])

    except Exception as e:
        st.error("Failed to fetch air quality data")
        st.exception(e)

 # -----------------------------
    # Color scale (simple AQI logic)
    # -----------------------------
    def color(pm):
        if pm < 10:
            return [0, 200, 0]      # good
        elif pm < 20:
            return [255, 200, 0]    # moderate
        elif pm < 30:
            return [255, 100, 0]    # unhealthy for sensitive
        else:
            return [200, 0, 0]      # unhealthy

    df["color"] = df["pm25"].apply(color)

    # -----------------------------
    # PyDeck interactive map
    # -----------------------------
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["lon", "lat"],
        get_fill_color="color",
        get_radius=20000,
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=df["lat"].mean(),
        longitude=df["lon"].mean(),
        zoom=4,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "PM2.5: {pm25}"}
    )

    st.pydeck_chart(deck)

'''
ROOT = Path(__file__).resolve().parent
DOC = ROOT / "final_project" / "LCA_structuremodis_info.pdf"

# --- Setup ---
client = OpenAI(api_key="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")

st.title("📄 AI PDF Summarizer")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

# --- Helper: extract text ---
def extract_text(DOC):
    reader = PdfReader(DOC)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# --- Helper: chunk text ---
def chunk_text(text, chunk_size=3000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# --- Helper: summarize chunk ---
def summarize_chunk(chunk):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Summarize the following text concisely."},
            {"role": "user", "content": chunk}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

# --- Main logic ---
if uploaded_file:

    with st.spinner("Extracting text..."):
        text = extract_text(uploaded_file)

    if not text.strip():
        st.error("Could not extract text from PDF.")
        st.stop()

    st.success("Text extracted!")

    if st.button("Generate Summary"):

        chunks = chunk_text(text)

        summaries = []

        with st.spinner("Summarizing..."):
            for chunk in chunks:
                summaries.append(summarize_chunk(chunk))

        # --- Final summary ---
        final_summary = summarize_chunk(" ".join(summaries))

        st.subheader("🧠 Summary")
        st.write(final_summary)

        # Optional: expandable detailed summaries
        with st.expander("📚 Section summaries"):
            for i, s in enumerate(summaries):
                st.write(f"**Part {i+1}**")
                st.write(s)
'''