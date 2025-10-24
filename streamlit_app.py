import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import random

# --- Configuration ---
st.set_page_config(
    page_title="Bikeroom Sales Dashboard (Price Trend Edition)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Generation Function (Mock Data) ---
@st.cache_data
def load_data():
    """
    Generates mock bike sales data (Granular).
    We keep the date and price for each transaction to enable time-series analysis.
    """
    num_rows = 1000
    
    # Define data fields
    models = ['Speedster 3000', 'Trail King Pro', 'City Commuter E-3', 'Gravel Explorer', 'Aero Blade Race']
    categories = ['Road', 'Mountain', 'City', 'Electric', 'BMX']
    regions = ['North America', 'Europe', 'Asia', 'Oceania']
    
    data = {
        'Bike_Model': [np.random.choice(models, p=[0.25, 0.20, 0.30, 0.15, 0.10]) for _ in range(num_rows)],
        'Category': [random.choice(categories) for _ in range(num_rows)],
        # Price is generated with noise to simulate fluctuations over time
        'Price_USD': np.round(np.random.normal(loc=1800, scale=700, size=num_rows), -1).clip(500, 6000),
        'Units_Sold': np.random.randint(1, 50, num_rows),
        'Region': [random.choice(regions) for _ in range(num_rows)],
        # Distribute sales randomly across the year
        'Date': pd.to_datetime('2024-01-01') + pd.to_timedelta(np.random.randint(0, 365, num_rows), unit='D')
    }
    
    granular_df = pd.DataFrame(data)
    granular_df['Total_Sales_USD'] = granular_df['Price_USD'] * granular_df['Units_Sold']
    
    # Sort by date for better time-series charting
    granular_df.sort_values('Date', inplace=True)
    return granular_df

# Load the granular data
granular_sales_df = load_data()

# --- Title and Introduction ---
st.title("📈 Bikeroom Sales Dashboard: Price Trend Analysis")
st.markdown("""
This dashboard focuses on visualizing price changes over time using mock, granular sales data. 
Use the filters in the sidebar to examine trends for specific categories.
""")


# --- Sidebar for User Input ---
st.sidebar.header("Filter Sales Data")

# Filter 1: Category Multiselect
selected_categories = st.sidebar.multiselect(
    'Select Bike Category',
    options=granular_sales_df['Category'].unique(),
    default=granular_sales_df['Category'].unique()
)

# Filter 2: Price Slider (Now filtering on individual transaction price)
min_price = st.sidebar.slider(
    'Minimum Individual Sale Price ($)',
    float(granular_sales_df['Price_USD'].min()),
    float(granular_sales_df['Price_USD'].max()),
    float(granular_sales_df['Price_USD'].min())
)

# --- Data Filtering ---
# Filter the granular data based on user selections
filtered_df = granular_sales_df[
    (granular_sales_df['Category'].isin(selected_categories)) &
    (granular_sales_df['Price_USD'] >= min_price)
]

# --- Main Content Layout ---

# 1. KPIs (Calculated from the filtered granular data)
total_revenue = filtered_df['Total_Sales_USD'].sum()
total_units = filtered_df['Units_Sold'].sum()

st.subheader("Key Performance Indicators (KPIs)")
col_kpi_1, col_kpi_2, col_kpi_3 = st.columns(3)

col_kpi_1.metric("Total Filtered Revenue", f"${total_revenue:,.0f}")
col_kpi_2.metric("Total Units Sold", f"{total_units:,.0f}")
col_kpi_3.metric(
    "Average Price per Unit", 
    f"${total_revenue / (total_units or 1):,.2f}",
    delta=f"Based on {len(filtered_df)} transactions"
)

st.markdown("---")

# 2. NEW: Price Change Visualization (Time Series)
st.header("Price Trend Analysis")
st.subheader("Monthly Average Price per Unit by Category")

if not filtered_df.empty:
    # Aggregate filtered data by month and category to get mean price
    df_time_series = filtered_df.set_index('Date')
    
    # Resample monthly and calculate the mean price
    price_trend = df_time_series.groupby('Category')['Price_USD'].resample('M').mean().reset_index()
    price_trend.rename(columns={'Price_USD': 'Avg_Price'}, inplace=True)

    # Altair Line Chart for Price Trend
    chart_price = alt.Chart(price_trend).mark_line(point=True).encode(
        x=alt.X('Date', axis=alt.Axis(title='Date', format='%Y-%m')),
        y=alt.Y('Avg_Price', axis=alt.Axis(title='Average Price (USD)', format='$,.0f')),
        color='Category',
        tooltip=['Date', 'Category', alt.Tooltip('Avg_Price', format='$,.2f')]
    ).properties(
        title='Average Monthly Price Trend'
    ).interactive() # Add interactive for zoom/pan

    st.altair_chart(chart_price, use_container_width=True)
else:
    st.warning("No data matches the current filter criteria for charting.")


st.markdown("---")


# 3. Supporting Visualizations (Now calculated from filtered granular data)
st.header("Sales Volume & Distribution")

col_viz_1, col_viz_2 = st.columns(2)

with col_viz_1:
    st.subheader("Total Units Sold by Bike Category")
    
    if not filtered_df.empty:
        # Aggregate on the fly
        units_by_category = filtered_df.groupby('Category')['Units_Sold'].sum().reset_index()
        
        # Altair Bar Chart
        chart_units = alt.Chart(units_by_category).mark_bar().encode(
            x=alt.X('Category', sort='-y'),
            y=alt.Y('Units_Sold', title='Total Units Sold'),
            tooltip=['Category', 'Units_Sold']
        ).properties(
            height=300
        ).interactive()
        
        st.altair_chart(chart_units, use_container_width=True)
    else:
        st.warning("No data for Units by Category.")

with col_viz_2:
    st.subheader("Revenue Distribution by Region")
    
    if not filtered_df.empty:
        # Aggregate on the fly
        revenue_by_region = filtered_df.groupby('Region')['Total_Sales_USD'].sum().reset_index()
        
        # Altair Pie/Donut Chart for Revenue Share
        base = alt.Chart(revenue_by_region).encode(
            theta=alt.Theta("Total_Sales_USD:Q", stack=True)
        )
        
        pie = base.mark_arc(outerRadius=120, innerRadius=50).encode(
            color=alt.Color("Region:N"),
            order=alt.Order("Total_Sales_USD:Q", sort="descending"),
            tooltip=["Region", alt.Tooltip('Total_Sales_USD', format='$,.0f')]
        ).properties(
            title='Revenue Share by Region'
        )
        
        st.altair_chart(pie, use_container_width=True)
    else:
        st.warning("No data for Revenue by Region.")


# 4. Detailed Data Table
st.header("Detailed Sales Transactions")
st.markdown(f"**Showing {len(filtered_df)} individual transactions** matching your filters.")
# Display the granular data table
st.dataframe(filtered_df, use_container_width=True)


# --- Deployment Instructions Footer ---
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    ### Deployment Status: Ready!
    1. **Commit** the updated `streamlit_app.py` and `requirements.txt` to your GitHub repo.
    2. **Deploy** on [Streamlit Cloud](https://share.streamlit.io/).
    """
)
