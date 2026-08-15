import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(
    page_title="NBA Player Value Analytics",
    page_icon="🏀",
    layout="wide"
)

# Title
st.title("🏀 NBA Player Value Analytics")

st.write(
    "Analyzing NBA player performance relative to salary "
    "to identify the league's strongest contract values."
)

st.divider()

# Load leaderboard
df = pd.read_csv("nba_value_leaderboard.csv")

# Section title
st.header("NBA Value Leaderboard")

st.write(
    "Players are ranked using offensive value, defensive value, "
    "availability, overall performance, and salary-adjusted value."
)

# Display leaderboard
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
