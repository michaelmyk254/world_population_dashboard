import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Global Statistics", page_icon="🗺️")

st.title("🗺️ Global Statistics")
st.markdown("Explore global population statistics, rankings, and continental data")

# Get data from session state
df_long_with_world = st.session_state.df_long_with_world
template = st.session_state.get("template", "plotly")

# Sidebar filters
st.sidebar.header("🔎 Filter Options")

# Year selection
year_min = int(df_long_with_world["Year"].min())
year_max = int(df_long_with_world["Year"].max())

selected_year = st.sidebar.slider(
    "Select Year",
    year_min,
    year_max,
    year_max
)

# Get data for selected year
year_data = df_long_with_world[df_long_with_world["Year"] == selected_year].copy()

# SECTION 1: TOP 10 COUNTRIES BAR CHART
st.subheader(f"🏆 Top 10 Most Populous Countries ({selected_year})")

top_10 = year_data[year_data["Country"] != "World"].nlargest(10, "Population")

fig_top10 = px.barh(
    top_10.sort_values("Population"),
    y="Country",
    x="Population",
    title=f"Top 10 Most Populous Countries in {selected_year}",
    color="Population",
    color_continuous_scale="Viridis",
    template=template
)

fig_top10.update_layout(
    height=400,
    showlegend=False
)

st.plotly_chart(fig_top10, use_container_width=True)

# SECTION 2: CONTINENTAL STATISTICS
st.subheader(f"🌍 Population by Continent ({selected_year})")

continental_data = year_data[year_data["Country"] != "World"].groupby("Continent")["Population"].sum().reset_index()
continental_data = continental_data.sort_values("Population", ascending=False)

col1, col2 = st.columns(2)

with col1:
    fig_bar = px.bar(
        continental_data,
        x="Continent",
        y="Population",
        title=f"Total Population by Continent",
        color="Population",
        color_continuous_scale="Blues",
        template=template
    )
    
    fig_bar.update_layout(height=400)
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    fig_pie = px.pie(
        continental_data,
        values="Population",
        names="Continent",
        title=f"Population Distribution by Continent",
        template=template
    )
    
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

# SECTION 3: CONTINENTAL STATISTICS TABLE
st.subheader(f"📊 Continental Statistics ({selected_year})")

continental_stats = []
total_world_pop = year_data[year_data["Country"] != "World"]["Population"].sum()

for continent in continental_data["Continent"]:
    continent_pop = continental_data[continental_data["Continent"] == continent]["Population"].values[0]
    percentage = (continent_pop / total_world_pop) * 100
    countries_count = year_data[(year_data["Continent"] == continent) & (year_data["Country"] != "World")].shape[0]
    
    continental_stats.append({
        "Continent": continent,
        "Total Population": int(continent_pop),
        "% of World": f"{percentage:.2f}%",
        "Countries": countries_count
    })

stats_df = pd.DataFrame(continental_stats)
st.dataframe(stats_df, use_container_width=True)

# SECTION 4: GLOBAL TRENDS
st.subheader("📈 Global Population Growth Trends")

years_to_plot = df_long_with_world[df_long_with_world["Country"] == "World"].sort_values("Year")

fig_global = px.line(
    years_to_plot,
    x="Year",
    y="Population",
    title="World Population Growth Over Time",
    markers=True,
    template=template
)

fig_global.update_layout(height=400)
st.plotly_chart(fig_global, use_container_width=True)

# SECTION 5: TOP GROWING COUNTRIES
st.subheader(f"📈 Fastest Growing Countries ({selected_year})")

growth_data = year_data[year_data["Country"] != "World"].copy()
growth_data = growth_data.dropna(subset=["Growth_Rate"])
growth_data = growth_data.sort_values("Growth_Rate", ascending=False).head(10)

if not growth_data.empty:
    fig_growth = px.barh(
        growth_data.sort_values("Growth_Rate"),
        y="Country",
        x="Growth_Rate",
        title=f"Top 10 Fastest Growing Countries ({selected_year})",
        color="Growth_Rate",
        color_continuous_scale="Reds",
        template=template
    )
    
    fig_growth.update_layout(height=400)
    st.plotly_chart(fig_growth, use_container_width=True)

# SECTION 6: GLOBAL SUMMARY METRICS
st.subheader("🌐 Global Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    world_pop = year_data[year_data["Country"] == "World"]["Population"].values
    if len(world_pop) > 0:
        st.metric("World Population", f"{int(world_pop[0]):,}")

with col2:
    countries_count = year_data[year_data["Country"] != "World"].shape[0]
    st.metric("Countries/Territories", countries_count)

with col3:
    continents_count = year_data[year_data["Country"] != "World"]["Continent"].nunique()
    st.metric("Continents", continents_count)

with col4:
    avg_growth = year_data[year_data["Country"] != "World"]["Growth_Rate"].mean()
    if pd.notna(avg_growth):
        st.metric("Avg. Growth Rate", f"{avg_growth:.2f}%")

# SECTION 7: CONTINENTAL GROWTH TRENDS
st.subheader("📊 Continental Growth Trends Over Time")

# Calculate population by continent for each year
continental_trends = df_long_with_world[df_long_with_world["Country"] != "World"].groupby(
    ["Year", "Continent"]
)["Population"].sum().reset_index()

fig_continental_trends = px.line(
    continental_trends,
    x="Year",
    y="Population",
    color="Continent",
    title="Population Growth by Continent Over Time",
    markers=True,
    template=template
)

fig_continental_trends.update_layout(height=400)
st.plotly_chart(fig_continental_trends, use_container_width=True)
