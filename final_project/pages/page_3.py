import streamlit as st



st.title("Windy layers")
st.subheader("Get key-insights about the consequences of these fires")

layer = st.selectbox("Select Wind Layer", ["wind", "rain", "temp", "clouds", "pressure"])

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <style>
        #windy { width: 100%; height: 500px; }
    </style>
</head>
<body>

<div id="windy"></div>

<!-- 1. Leaflet JS (required) -->
<script src="https://unpkg.com/leaflet@1.4.0/dist/leaflet.js"></script>

<!-- 2. Windy API -->
<script src="https://api.windy.com/assets/map-forecast/libBoot.js"></script>

<script>
const options = {
    key: 'IEYLuC8wRBBNg42tIs85sxNGYX3bgb7i',
    lat: -25,
    lon: 135,
    zoom: 4,
};

windyInit(options, windyAPI => {
    const { map } = windyAPI;

    windyAPI.store.set('overlay', '{layer}');
});
</script>

</body>
</html>
"""

st.components.v1.html(html_code, height=500)