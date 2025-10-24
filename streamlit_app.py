import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# --- Configuration ---
st.set_page_config(
    page_title="Bikeroom Sales Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Generation Function (Mock Data) ---
@st.cache_data
def load_data():
    """Generates mock bike sales and inventory data."""
    num_rows = 1000
    
    # Define data fields
    models = ['Speedster 3000', 'Trail King Pro', 'City Commuter E-3', 'Gravel Explorer', 'Aero Blade Race']
    categories = ['Road', 'Mountain', 'City', 'Electric', 'BMX']
    regions = ['North America', 'Europe', 'Asia', 'Oceania']
    
    data = {
        'Bike_Model': [np.random.choice(models, p=[0.25, 0.20, 0.30, 0.15, 0.10]) for _ in range(num_rows)],
        'Category': [random.choice(categories) for _ in range(num_rows)],
        'Price_USD': np.round(np.random.normal(loc=1800, scale=700, size=num_rows), -1).clip(500, 6000),
        'Units_Sold': np.random.randint(1, 50, num_rows),
        'Region': [random.choice(regions) for _ in range(num_rows)],
        'Date': pd.to_datetime('2024-01-01') + pd.to_timedelta(np.random.randint(0, 365, num_rows), unit='D')
    }
    
    df = pd.DataFrame(data)
    df['Total_Sales_USD'] = df['Price_USD'] * df['Units_Sold']
    
    # Aggregate sales data by model and region for cleaner visualization
    aggregated_df = df.groupby(['Bike_Model', 'Category', 'Region']).agg(
        Total_Units=('Units_Sold', 'sum'),
        Total_Revenue=('Total_Sales_USD', 'sum')
    ).reset_index()
    
    return aggregated_df

bike_sales_df = load_data()

# --- Title and Introduction ---
st.title("🚲 Bikeroom Sales Dashboard")
st.markdown("""
A ready-to-deploy Streamlit application demonstrating sales analysis on mock bicycle data. 
Use the sidebar filters to explore revenue and unit sales by category and region.
""")


# --- Sidebar for User Input ---
st.sidebar.header("Filter Sales Data")

# Filter 1: Category Multiselect
selected_categories = st.sidebar.multiselect(
    'Select Bike Category',
    options=bike_sales_df['Category'].unique(),
    default=bike_sales_df['Category'].unique()
)

# Filter 2: Price Slider (using Total Revenue as a proxy for value filtering)
min_revenue = st.sidebar.slider(
    'Minimum Total Revenue ($)',
    float(bike_sales_df['Total_Revenue'].min()),
    float(bike_sales_df['Total_Revenue'].max()),
    float(bike_sales_df['Total_Revenue'].min())
)

# --- Data Filtering ---
filtered_df = bike_sales_df[
    (bike_sales_df['Category'].isin(selected_categories)) &
    (bike_sales_df['Total_Revenue'] >= min_revenue)
]

# --- Main Content Layout ---

# 1. KPIs
total_revenue = filtered_df['Total_Revenue'].sum()
total_units = filtered_df['Total_Units'].sum()

st.subheader("Key Performance Indicators (KPIs)")
col_kpi_1, col_kpi_2, col_kpi_3 = st.columns(3)

col_kpi_1.metric(
    "Total Filtered Revenue", 
    f"${total_revenue:,.0f}",
    delta=f"Showing {len(filtered_df)} data points"
)
col_kpi_2.metric(
    "Total Units Sold", 
    f"{total_units:,.0f}"
)
col_kpi_3.metric(
    "Average Price per Unit", 
    f"${total_revenue / (total_units or 1):,.2f}"
)

st.markdown("---")


# 2. Visualizations
st.header("Sales Distribution")

col_viz_1, col_viz_2 = st.columns(2)

with col_viz_1:
    st.subheader("Total Units Sold by Bike Category")
    
    if not filtered_df.empty:
        units_by_category = filtered_df.groupby('Category')['Total_Units'].sum().reset_index()
        
        # Altair Bar Chart
        chart_units = alt.Chart(units_by_category).mark_bar().encode(
            x=alt.X('Category', sort='-y'),
            y=alt.Y('Total_Units'),
            tooltip=['Category', 'Total_Units']
        ).properties(
            height=300
        ).interactive()
        
        st.altair_chart(chart_units, use_container_width=True)
    else:
        st.warning("No data matches the current filter criteria for charting.")

with col_viz_2:
    st.subheader("Revenue Distribution by Region")
    
    if not filtered_df.empty:
        revenue_by_region = filtered_df.groupby('Region')['Total_Revenue'].sum().reset_index()
        
        # Altair Pie/Donut Chart for Revenue Share
        base = alt.Chart(revenue_by_region).encode(
            theta=alt.Theta("Total_Revenue:Q", stack=True)
        )
        
        pie = base.mark_arc(outerRadius=120, innerRadius=50).encode(
            color=alt.Color("Region:N"),
            order=alt.Order("Total_Revenue:Q", sort="descending"),
            tooltip=["Region", alt.Tooltip('Total_Revenue', format='$,.0f')]
        ).properties(
            title='Revenue Share by Region'
        )
        
        st.altair_chart(pie, use_container_width=True)
    else:
        st.warning("No data to display in the chart.")


# 3. Detailed Data Table
st.header("Detailed Sales Records")
st.markdown(f"**Showing {len(filtered_df)} records** (aggregated by Model, Category, and Region).")
st.dataframe(filtered_df, use_container_width=True)


# --- Deployment Instructions Footer ---
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    ### Deployment Status: Ready!
    1. **Commit** the new `streamlit_app.py` and `requirements.txt` to your GitHub repo.
    2. **Deploy** on [Streamlit Cloud](https://share.streamlit.io/).
    """
)
