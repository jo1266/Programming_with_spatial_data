import streamlit as st



st.title("Windy layers")
st.subheader("Get key-insights about the consequences of these fires")

layer = st.selectbox("Select Wind Layer", ["no2", "aod550", "tcso2", "drought40", "fwi", "temp"])

st.subheader("🔎 Data Check")

if "selected_country" not in st.session_state:
    st.warning("Missing selected country.")
    st.stop()

if "country_bounds" not in st.session_state:
    st.warning("Country bounds not available.")
    st.stop()


minx = st.session_state["country_bounds"]["minx"]
miny = st.session_state["country_bounds"]["miny"]
maxx = st.session_state["country_bounds"]["maxx"]
maxy = st.session_state["country_bounds"]["maxy"]


center_lat = (miny + maxy) / 2
center_lon = (minx + maxx) / 2

# crude zoom estimation based on bbox size
lat_range = abs(maxy - miny)
lon_range = abs(maxx - minx)
max_range = max(lat_range, lon_range)

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
                console.log("Layer:", '{layer}');
                store.set('overlay', "{layer}");
            }}, 3000);
        }});
    }});
}});


</script>

</body>
</html>
"""

st.components.v1.html(html_code, height=500)