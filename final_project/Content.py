import streamlit as st
from pathlib import Path

st.title("Programming with Spatial Data: Final Project")

st.header("Introduction")
st.write("The National Aeronautics ans Space Administration (NASA) provide the general public with" \
"multiple up-to-date databases. Among these, the Fire Information for Resource Management System (FIRMS)" \
"conatains information about live wildfires occuring world-wide. The focus here is put on western Europe" \
"as the wild fires season has already started.")

st.subheader("FRIMS resource by NASA")

#ROOT = Path(__file__).resolve().parent
#PIC = ROOT / "figures" / "LCA_structure.png"

st.video("https://www.youtube.com/watch?v=EZMACTAg4v0")

st.header("About this App")
st.write("""
This app serves to:
- Fetch the data from the FIRMS and summarize it smartly.
- Visualize where the wildfires are actually happening across Europe.
- 
""")

st.subheader("Navigation")
st.write("Use the sidebar on the left to switch between pages.")