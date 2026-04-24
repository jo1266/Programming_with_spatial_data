import streamlit as st



st.title("Windy layers")
st.subheader("Get key-insights about the consequences of these fires")

layer = st.selectbox("Select Wind Layer", ["no2", "aod550", "tcso2", "drought40", "fwi", "temp"])

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
    lat: -25,
    lon: 135,
    zoom: 4,
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