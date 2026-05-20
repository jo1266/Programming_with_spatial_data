import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
import numpy as np


st.title("Potential wildfires consequences")

st.subheader("Live windy data")

# Data availability check
if "selected_country" not in st.session_state:
    st.warning("Missing selected country.")
    st.stop()

if "country_bounds" not in st.session_state:
    st.warning("Country bounds not available.")
    st.stop()

st.info("Select the desired layer on the top right corner of the map")

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

# Fetching windy map via API
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <style>
        #windy {{ width: 100%; height: 500px; }}
    </style>
</head>
<body>

<div id="windy"></div>

<!-- 1. Leaflet JS (required) -->
<script src="https://unpkg.com/leaflet@1.4.0/dist/leaflet.js"></script>

<!-- 2. Windy API -->
<script src="https://api.windy.com/assets/map-forecast/libBoot.js"></script>

<script>
const options = {{
    key: '6awPyqRUyngI5NYlPJkQVziDwYs8jUZ6',
    lat: {center_lat},
    lon: {center_lon},
    zoom: {zoom},
}};

windyInit(options, windyAPI => {{
    const {{ store }} = windyAPI;
    store.on('ready', () => {{
        requestAnimationFrame(() => {{
            setTimeout(() => {{
                console.log("Layer:", 'layer');
                store.set('overlay', "layer");
            }}, 3000);
        }});
    }});
}});


</script>

</body>
</html>
"""

# Windy map visualization
st.components.v1.html(html_code, height=500)

st.subheader("Air Quality Visualization")

VARIABLES = {
    "Carbon Dioxide (CO2)": "carbon_dioxide",
    "Carbon Monoxide (CO)": "carbon_monoxide",
    "Nitrogen Dioxide (NO2)": "nitrogen_dioxide",
    "Sulphur Dioxide (SO2)": "sulphur_dioxide",
    "Methane (CH4)": "methane",
    "Fine particules (<2.5 microns)": "pm2_5"
}

def generate_grid(minx, miny, maxx, maxy, n):
    lons = np.linspace(minx, maxx, n)
    lats = np.linspace(miny, maxy, n)

    points = []
    for lat in lats:
        for lon in lons:
            points.append((lat, lon))
    return points

grid_points = generate_grid(minx, miny, maxx, maxy, n=10)

selected_var_label = st.selectbox(
    "Select an air quality variable",
    list(VARIABLES.keys())
)

selected_var = VARIABLES[selected_var_label]

# -----------------------------
# Fetch AQ data
# -----------------------------
@st.cache_data
def fetch_point(lat, lon, var):
    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&hourly={var}"
        "&timezone=auto"
    )
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()

    # take latest value
    value = data["hourly"][var][-1]

    return value

data_points = []

if st.button("Generate Air Quality Map"):

    with st.spinner("Fetching air quality data..."):

        for lat, lon in grid_points:
            try:
                value = fetch_point(lat, lon, selected_var)

                data_points.append({
                    "lat": lat,
                    "lon": lon,
                    "value": value
                })

            except:
                continue

    df = pd.DataFrame(data_points)

    st.success("Air Quality Data loaded")

    st.dataframe(df)

    # Error handling
    if df.empty or df["value"].isna().all():
        st.warning("No data is available to build the concentration map")
        st.stop()

 # -----------------------------
    # Color scale (simple AQI logic)
    # -----------------------------
    vmin, vmax = df["value"].min(), df["value"].max()

    def color_scale(v):
        norm = (v - vmin) / (vmax - vmin + 1e-6)

        # green → yellow → red
        return [
            int(255 * norm),
            int(255 * (1 - norm)),
            80
        ]

    df["color"] = df["value"].apply(color_scale)

    # -----------------------------
    # PyDeck interactive map
    # -----------------------------
    st.info("Hover over points to get the current concentration")

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["lon", "lat"],
        get_fill_color="color",
        get_radius=5000,
        radius_units="meters",
        radius_min_pixels=1,
        radius_max_pixels=10,
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
        tooltip={"text": f"{selected_var_label}: {{value}}"}
    )

    st.pydeck_chart(deck)