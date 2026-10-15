import streamlit as st

st.set_page_config(page_title="Rotation schedule", layout="wide")

pages = [
    st.Page("views/template.py", title="24-week template", default=True),
    st.Page("views/actual_dates.py", title="Rotation by date"),
    st.Page("views/akso_departures.py", title="AKSO Departures"),
]

st.navigation(pages).run()
