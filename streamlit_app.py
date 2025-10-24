import streamlit as st
import pandas as pd
import numpy as np
import altair as alt # Moved import to the top for clarity and best practice
from sklearn.datasets import load_iris

# --- Configuration ---
# Set the page configuration for a wide layout
st.set_page_config(
    page_title="Streamlit Data Explorer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Loading (Cached for performance) ---
@st.cache_data
def load_data():
    """Loads the Iris dataset from scikit-learn."""
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df['species'] = iris.target_names[iris.target]
    return df

iris_df = load_data()

# --- Title and Introduction ---
st.title("🌱 Streamlit Data Explorer: Iris Dataset")

st.markdown("""
Welcome to a simple, ready-to-deploy Streamlit application! This app allows you to explore the classic Iris dataset 
by filtering the data and visualizing feature distributions.
""")

# --- Sidebar for User Input ---
st.sidebar.header("User Input Controls")

# Create a slider to filter data based on Sepal Length
sepal_length_min = st.sidebar.slider(
    'Minimum Sepal Length (cm)',
    float(iris_df['sepal length (cm)'].min()),
    float(iris_df['sepal length (cm)'].max()),
    float(iris_df['sepal length (cm)'].min()) + 1.0  # Set a default value slightly higher than min
)

# Create a multiselect for species filtering
selected_species = st.sidebar.multiselect(
    'Select Species to Display',
    options=iris_df['species'].unique(),
    default=iris_df['species'].unique()
)

# --- Data Filtering ---
filtered_df = iris_df[
    (iris_df['sepal length (cm)'] >= sepal_length_min) &
    (iris_df['species'].isin(selected_species))
]

# --- Main Content Layout ---
st.header("Filtered Data View")
st.markdown(f"**Showing {len(filtered_df)} of {len(iris_df)} records** based on your selections.")

# Display the filtered data table
st.dataframe(filtered_df, use_container_width=True)


# --- Visualization ---
st.header("Feature Visualization")

# Use two columns for better layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribution of Petal Width")
    
    # Check if there is data to plot
    if not filtered_df.empty:
        # Create a histogram using Streamlit's built-in chart capabilities
        st.bar_chart(filtered_df['petal width (cm)'].value_counts().sort_index())
    else:
        st.warning("No data matches the current filter criteria.")

with col2:
    st.subheader("Species Count")
    
    if not filtered_df.empty:
        # Pie chart showing the distribution of the remaining species
        species_counts = filtered_df['species'].value_counts().reset_index()
        species_counts.columns = ['Species', 'Count']
        
        # Use Streamlit's built-in altair chart for a cleaner pie chart (using a simple donut approach)
        base = alt.Chart(species_counts).encode(
            theta=alt.Theta("Count:Q", stack=True)
        )

        pie = base.mark_arc(outerRadius=120, innerRadius=50).encode(
            color=alt.Color("Species:N"),
            order=alt.Order("Count:Q", sort="descending"),
            tooltip=["Species", "Count"]
        )
        
        st.altair_chart(pie, use_container_width=True)
    else:
        st.warning("No data to display in the chart.")


# --- Deployment Instructions Footer ---
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Deployment Steps:**
    1. Commit these two files (`streamlit_app.py` and `requirements.txt`) to a new GitHub repository.
    2. Go to [Streamlit Cloud](https://share.streamlit.io/).
    3. Click "New app" and point it to your GitHub repository and the file path (`streamlit_app.py`).
    """
)
