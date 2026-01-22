import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Country Overview", page_icon="🌍")

st.title("🌍 Country Overview")
st.markdown("Select a country to view detailed population statistics and trends")

# Get data from session state
df_long = st.session_state.df_long
df_long_with_world = st.session_state.df_long_with_world
template = st.session_state.get("template", "plotly")

# Sidebar filters
st.sidebar.header("🔎 Filter Options")

# Continent/Region filter
continents = sorted(df_long['Continent'].unique())
selected_continent = st.sidebar.selectbox(
    "Filter by Continent (optional)",
    ["All Continents"] + continents
)

# Get countries based on continent selection
if selected_continent == "All Continents":
    countries = sorted(df_long_with_world["Country"].unique())
else:
    countries = sorted(df_long_with_world[df_long_with_world["Continent"] == selected_continent]["Country"].unique())

# Single country selection
default_index = countries.index("Kenya") if "Kenya" in countries else 0
selected_country = st.sidebar.selectbox(
    "Select Primary Country",
    countries,
    index=default_index
)

# Year range slider
year_min = int(df_long["Year"].min())
year_max = int(df_long["Year"].max())

year_range = st.sidebar.slider(
    "Select Year Range",
    year_min,
    year_max,
    (year_min, year_max)
)

# Export option
export_format = st.sidebar.selectbox(
    "📥 Export Chart Format",
    ["PNG", "SVG", "HTML"]
)

# Filter dataframe for primary country
filtered_df = df_long[
    (df_long["Country"] == selected_country) &
    (df_long["Year"] >= year_range[0]) &
    (df_long["Year"] <= year_range[1])
].sort_values("Year")

if not filtered_df.empty:
    # SECTION 1: METRICS
    st.subheader(f"📊 {selected_country} Population Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    latest_population = filtered_df.iloc[-1]["Population"]
    latest_year = int(filtered_df.iloc[-1]["Year"])
    earliest_population = filtered_df.iloc[0]["Population"]
    total_growth = ((latest_population - earliest_population) / earliest_population) * 100
    
    with col1:
        st.metric(
            label=f"Current Population ({latest_year})",
            value=f"{int(latest_population):,}"
        )
    
    with col2:
        st.metric(
            label="Total Growth",
            value=f"{total_growth:.2f}%"
        )
    
    with col3:
        growth_rate = filtered_df.iloc[-1]["Growth_Rate"]
        if pd.notna(growth_rate):
            st.metric(
                label="Recent Growth Rate",
                value=f"{growth_rate:.2f}%"
            )
    
    with col4:
        population_change = latest_population - earliest_population
        st.metric(
            label="Total Change",
            value=f"{int(population_change):,}"
        )
    
    # SECTION 2: POPULATION TREND CHART
    st.subheader(f"📈 Population Trend: {selected_country}")
    
    fig_line = px.line(
        filtered_df,
        x="Year",
        y="Population",
        title=f"Population Growth Trend: {selected_country}",
        markers=True,
        template=template
    )
    
    fig_line.update_layout(
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig_line, use_container_width=True)
    
    # Export chart
    if st.button(f"📥 Export {selected_country} Chart as {export_format}"):
        try:
            if export_format == "PNG":
                img_bytes = fig_line.to_image(format="png")
                st.download_button(
                    label=f"Download PNG",
                    data=img_bytes,
                    file_name=f"{selected_country}_population.png",
                    mime="image/png"
                )
            elif export_format == "SVG":
                svg_bytes = fig_line.to_image(format="svg")
                st.download_button(
                    label=f"Download SVG",
                    data=svg_bytes,
                    file_name=f"{selected_country}_population.svg",
                    mime="image/svg+xml"
                )
            elif export_format == "HTML":
                html = fig_line.to_html()
                st.download_button(
                    label=f"Download HTML",
                    data=html,
                    file_name=f"{selected_country}_population.html",
                    mime="text/html"
                )
        except Exception as e:
            st.warning(f"Export failed: {str(e)}")
    
    # SECTION 3: GROWTH RATE CHART
    st.subheader(f"📊 Population Growth Rate: {selected_country}")
    
    growth_data = filtered_df.dropna(subset=['Growth_Rate'])
    
    if not growth_data.empty:
        fig_growth = px.bar(
            growth_data,
            x="Year",
            y="Growth_Rate",
            title=f"Annual Growth Rate: {selected_country}",
            color="Growth_Rate",
            color_continuous_scale="RdYlGn",
            template=template
        )
        
        fig_growth.update_layout(height=300)
        st.plotly_chart(fig_growth, use_container_width=True)
    
    # SECTION 4: DATA TABLE
    st.subheader("📄 Population Data Table")
    
    display_df = filtered_df[['Year', 'Population', 'Growth_Rate']].copy()
    display_df['Population'] = display_df['Population'].astype(int)
    display_df['Growth_Rate'] = display_df['Growth_Rate'].round(2)
    
    st.dataframe(display_df, use_container_width=True)
    
else:
    st.warning("No data available for the selected filters.")
