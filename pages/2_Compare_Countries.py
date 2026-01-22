import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Compare Countries", page_icon="🌐")

st.title("🌐 Compare Countries")
st.markdown("Compare population trends across multiple countries")

# Get data from session state
df_long_with_world = st.session_state.df_long_with_world
template = st.session_state.get("template", "plotly")

# Sidebar filters
st.sidebar.header("🔎 Comparison Options")

# Countries selection
all_countries = sorted(df_long_with_world["Country"].unique())

# Default selection - Kenya and World
default_countries = ["Kenya", "World"]
default_indices = [i for i, c in enumerate(all_countries) if c in default_countries]

selected_countries = st.sidebar.multiselect(
    "Select Countries to Compare",
    all_countries,
    default=default_countries
)

if not selected_countries:
    st.warning("Please select at least one country to compare.")
else:
    # Year range filter
    year_min = int(df_long_with_world["Year"].min())
    year_max = int(df_long_with_world["Year"].max())
    
    year_range = st.sidebar.slider(
        "Select Year Range",
        year_min,
        year_max,
        (year_min, year_max)
    )
    
    # Kenya vs World toggle
    show_kenya_world_ratio = st.sidebar.checkbox(
        "Show Kenya vs World Population Ratio",
        value=False
    )
    
    # Filter data
    comparison_df = df_long_with_world[
        (df_long_with_world["Country"].isin(selected_countries)) &
        (df_long_with_world["Year"] >= year_range[0]) &
        (df_long_with_world["Year"] <= year_range[1])
    ].sort_values("Year")
    
    # SECTION 1: COMPARISON CHART
    st.subheader(f"📈 Population Comparison: {', '.join(selected_countries)}")
    
    fig_comparison = px.line(
        comparison_df,
        x="Year",
        y="Population",
        color="Country",
        title="Population Trends Comparison",
        markers=True,
        template=template
    )
    
    fig_comparison.update_layout(
        hovermode='x unified',
        height=450
    )
    
    st.plotly_chart(fig_comparison, use_container_width=True)
    
    # SECTION 2: GROWTH RATE COMPARISON
    st.subheader("📊 Growth Rate Comparison")
    
    growth_comparison = comparison_df.dropna(subset=['Growth_Rate'])
    
    if not growth_comparison.empty:
        fig_growth_comp = px.line(
            growth_comparison,
            x="Year",
            y="Growth_Rate",
            color="Country",
            title="Annual Growth Rate Comparison",
            markers=True,
            template=template
        )
        
        fig_growth_comp.update_layout(height=350)
        st.plotly_chart(fig_growth_comp, use_container_width=True)
    
    # SECTION 3: KENYA VS WORLD RATIO (Optional)
    if show_kenya_world_ratio and "Kenya" in selected_countries and "World" in selected_countries:
        st.subheader("🌍 Kenya vs World: Population Ratio")
        
        kenya_data = comparison_df[comparison_df["Country"] == "Kenya"].copy()
        world_data = comparison_df[comparison_df["Country"] == "World"].copy()
        
        # Merge and calculate ratio
        ratio_data = pd.merge(
            kenya_data[["Year", "Population"]].rename(columns={"Population": "Kenya_Population"}),
            world_data[["Year", "Population"]].rename(columns={"Population": "World_Population"}),
            on="Year"
        )
        
        ratio_data["Kenya_as_%_of_World"] = (
            (ratio_data["Kenya_Population"] / ratio_data["World_Population"]) * 100
        ).round(2)
        
        fig_ratio = px.line(
            ratio_data,
            x="Year",
            y="Kenya_as_%_of_World",
            title="Kenya's Population as Percentage of World Population",
            markers=True,
            template=template
        )
        
        fig_ratio.update_layout(height=350)
        fig_ratio.update_yaxes(title_text="Percentage (%)")
        st.plotly_chart(fig_ratio, use_container_width=True)
        
        # Stats
        col1, col2 = st.columns(2)
        with col1:
            max_ratio = ratio_data["Kenya_as_%_of_World"].max()
            max_year = ratio_data.loc[ratio_data["Kenya_as_%_of_World"].idxmax(), "Year"]
            st.metric("Highest Ratio", f"{max_ratio:.2f}% ({int(max_year)})")
        
        with col2:
            current_ratio = ratio_data["Kenya_as_%_of_World"].iloc[-1]
            current_year = int(ratio_data["Year"].iloc[-1])
            st.metric(f"Current Ratio ({current_year})", f"{current_ratio:.2f}%")
    
    # SECTION 4: DATA TABLE
    st.subheader("📄 Comparison Data Table")
    
    table_df = comparison_df.pivot_table(
        index="Year",
        columns="Country",
        values="Population",
        aggfunc="first"
    ).astype(int)
    
    st.dataframe(table_df, use_container_width=True)
    
    # SECTION 5: STATISTICS SUMMARY
    st.subheader("📊 Summary Statistics")
    
    summary_data = []
    for country in selected_countries:
        country_data = comparison_df[comparison_df["Country"] == country]
        if not country_data.empty:
            summary_data.append({
                "Country": country,
                "Latest Year": int(country_data["Year"].max()),
                "Latest Population": int(country_data["Population"].max()),
                "Earliest Population": int(country_data["Population"].min()),
                "Growth": f"{((country_data['Population'].max() - country_data['Population'].min()) / country_data['Population'].min() * 100):.2f}%"
            })
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)
