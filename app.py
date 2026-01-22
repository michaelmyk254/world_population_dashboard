import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
import kaleido

# Initialize session state at the very beginning
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# Page configuration & Dark Mode
st.set_page_config(
    page_title="World Population Dashboard",
    page_icon="🌍",
    layout="wide"
)

# Title and Theme toggle
st.title("🌍 World Population Dashboard")

col1, col2 = st.columns([10, 1])
with col2:
    theme_display = "☀️" if st.session_state.theme == "light" else "🌙"
    if st.button(theme_display, help="Toggle Dark/Light Mode"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()

st.markdown("Interactive visualization of global population trends")

# Apply theme styling
if st.session_state.theme == "dark":
    template = "plotly_dark"
else:
    template = "plotly"

# Cache template in session state for pages
st.session_state.template = template

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("world_population.csv")
    return df

@st.cache_data
def calculate_growth_rate(population_data):
    """Calculate year-over-year growth rate"""
    if len(population_data) < 2:
        return None
    growth_rate = ((population_data.iloc[-1] - population_data.iloc[-2]) / population_data.iloc[-2]) * 100
    return growth_rate

@st.cache_data
def transform_data():
    """Transform data from wide to long format"""
    df_original = load_data()
    
    # Get all year columns (any column that ends with 'Population')
    year_columns = [col for col in df_original.columns if 'Population' in col and col != 'World Population Percentage']
    
    # Select relevant columns
    df_long = df_original[['Country', 'Continent'] + year_columns].copy()

    # Melt the dataframe
    df_long = pd.melt(
        df_long,
        id_vars=['Country', 'Continent'],
        value_vars=year_columns,
        var_name='Year',
        value_name='Population'
    )

    # Extract year from column name (e.g., "2022 Population" -> 2022)
    df_long['Year'] = df_long['Year'].str.extract(r'(\d{4})').astype(int)
    
    # Convert population to numeric, handling commas and other formats
    df_long['Population'] = pd.to_numeric(df_long['Population'], errors='coerce')
    
    # Drop rows with NaN populations
    df_long = df_long.dropna(subset=['Population']).copy()

    # Calculate growth rate
    df_long = df_long.sort_values(['Country', 'Year']).reset_index(drop=True)
    df_long['Growth_Rate'] = df_long.groupby('Country')['Population'].pct_change() * 100

    # Get world population data
    world_pop = df_long.groupby('Year')['Population'].sum().reset_index()
    world_pop['Country'] = 'World'
    world_pop['Continent'] = 'World'
    world_pop['Growth_Rate'] = world_pop['Population'].pct_change() * 100

    # Combine with world data
    df_long_with_world = pd.concat([df_long, world_pop], ignore_index=True)
    
    return df_original, df_long, df_long_with_world

# Transform and cache data
df_original, df_long, df_long_with_world = transform_data()

# Store in session state for access by pages
st.session_state.df_original = df_original
st.session_state.df_long = df_long
st.session_state.df_long_with_world = df_long_with_world

st.info("👈 Select a page from the sidebar to explore different sections of the dashboard!")
