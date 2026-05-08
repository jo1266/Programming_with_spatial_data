import streamlit as st
from pathlib import Path

st.title("Programming with Spatial Data: Final Project")

st.header("Introduction")
st.write("The National Aeronautics ans Space Administration (NASA) provide the general public with " \
"multiple up-to-date databases. Among these, the Fire Information for Resource Management System (FIRMS) " \
"contains information about live wildfires occuring world-wide. The focus here is put on western Europe " \
"as the wildfires season has already started.")

st.subheader("FRIMS resource by NASA")

st.video("https://www.youtube.com/watch?v=EZMACTAg4v0")

st.header("About this App")
st.write("""
This app serves to:
- Select a specific european country of interest.
- Fetch the data from the FIRMS and summarize it smartly.
- Visualize precisely where the wildfires are actually happening.
- Provide a live Windy map to show potential consequences of these fires.
""")

st.subheader("Navigation")
st.write("Use the sidebar on the left to switch between pages.")