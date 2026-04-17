import streamlit as st
from pathlib import Path

st.title("Programming with Spatial Data: final project")

st.header("Introduction")
st.write("Life Cycle Assessment (LCA) is widely used nowadyas to determine hotspots within supply chains of various industries in order to eventually reduce their environmental impacts as much as possible.")

st.subheader("LCA structure according to ISO 14040/44")

#ROOT = Path(__file__).resolve().parent
#PIC = ROOT / "figures" / "LCA_structure.png"

st.image(PIC, caption= "Source: Klöppfer and Grahl (2014)")

st.header("About this App")
st.write("""
This app serves to:
- Nicely display the results from my LCA case study
- Show some basic statistical descriptions to highlight that one unit process scoring low in a certain impact category doesn't necessarily score as low in another impact category
- Make the link with relevant economic instruments in a schematic way
""")

st.subheader("Navigation")
st.write("Use the sidebar on the left to switch between pages.")