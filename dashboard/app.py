# app.py
# Dashboard for Ethiopia Financial Inclusion: Historical Trends, Event Impacts, Forecasts
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# ----------------------------------------
# 1. Load Data
# ----------------------------------------
@st.cache_data
def load_data():
    data = pd.read_csv("data/processed/ethiopia_fi_enriched.csv", parse_dates=["observation_date"])
    impact = pd.read_csv("data/processed/impact_links_enriched.csv")
    forecasts = pd.read_csv("data/processed/ACC_OWNERSHIP_forecast_2025_2027.csv", index_col=0)
    return data, impact, forecasts

data, impact, forecasts = load_data()

# ----------------------------------------
# 2. Sidebar Navigation
# ----------------------------------------
st.sidebar.title("Ethiopia Financial Inclusion Dashboard")
page = st.sidebar.radio("Go to", ["Overview", "Trends", "Forecasts", "Inclusion Projections"])

# ----------------------------------------
# 3. Overview Page
# ----------------------------------------
if page == "Overview":
    st.title("Overview of Financial Inclusion")
    
    # Compute KPIs
    latest_year = data["observation_date"].dt.year.max()
    acc_latest = data.loc[(data["indicator_code"]=="ACC_OWNERSHIP") & 
                          (data["observation_date"].dt.year==latest_year), "value_numeric"].mean()
    dp_latest = data.loc[(data["indicator_code"]=="USG_DIGITAL_PAYMENT") & 
                         (data["observation_date"].dt.year==latest_year), "value_numeric"].mean()
    
    col1, col2 = st.columns(2)
    col1.metric("Account Ownership (Access)", f"{acc_latest:.1f}%")
    col2.metric("Digital Payment Usage", f"{dp_latest:.1f}%")
    
    st.subheader("Top Event Impacts")
    top_events = impact.groupby("parent_id")["impact_magnitude"].sum().sort_values(ascending=False).head(5)
    st.write(top_events)

# ----------------------------------------
# 4. Trends Page
# ----------------------------------------
elif page == "Trends":
    st.title("Historical Trends")
    
    indicator_select = st.selectbox("Select Indicator", ["ACC_OWNERSHIP", "USG_DIGITAL_PAYMENT"])
    filtered = data[data["indicator_code"]==indicator_select]
    
    fig = px.line(filtered, x="observation_date", y="value_numeric", color="gender",
                  markers=True, title=f"Historical Trend: {indicator_select}")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Event Impacts Overlay")
    event_filtered = impact[impact["related_indicator"]==indicator_select]
    if not event_filtered.empty:
        plt.figure(figsize=(10,4))
        sns.barplot(x="observation_date_event", y="impact_magnitude", data=event_filtered)
        plt.xticks(rotation=45)
        plt.title(f"Event Impacts on {indicator_select}")
        st.pyplot(plt.gcf())

# ----------------------------------------
# 5. Forecasts Page
# ----------------------------------------
elif page == "Forecasts":
    st.title("Forecasts (2025–2027)")
    
    scenario_select = st.selectbox("Select Scenario", forecasts.columns)
    fig = px.line(forecasts, x=forecasts.index, y=scenario_select, markers=True,
                  title=f"Forecast: {scenario_select}")
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------
# 6. Inclusion Projections Page
# ----------------------------------------
elif page == "Inclusion Projections":
    st.title("Financial Inclusion Projections")
    
    scenario_select = st.selectbox("Scenario", forecasts.columns)
    projection = forecasts[scenario_select]
    
    # Progress toward 60% target
    target = 60
    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(projection.index, projection.values, marker='o', label=f"{scenario_select} Forecast")
    ax.axhline(target, color='red', linestyle='--', label="60% Target")
    ax.set_title("Projected Account Ownership vs Target")
    ax.set_xlabel("Year")
    ax.set_ylabel("% of Adults")
    ax.legend()
    st.pyplot(fig)
    
    # Download button
    st.download_button(
        label="Download Forecast Data",
        data=projection.to_csv().encode('utf-8'),
        file_name=f"forecasts_{scenario_select}.csv",
        mime="text/csv"
    )
