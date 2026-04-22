import streamlit as st
import pandas as pd
from core.db import get_dashboard_data, mark_as_read

st.set_page_config(
    page_title="InsightEngine Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for premium look
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 2em;
        background-color: #4CAF50;
        color: white;
    }
    .stButton>button:hover {
        background-color: #45a049;
        border-color: #45a049;
    }
    .insight-card {
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
        background-color: #f9f9f9;
    }
    .score-badge {
        background-color: #1f77b4;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 InsightEngine: Daily Intelligence")

# Fetch data
data = get_dashboard_data()

# --- Sidebar Filters ---
st.sidebar.title("Filters")

if not data:
    st.info("No data available to filter.")
    sources = []
    types = []
else:
    # Convert Row objects to a DataFrame for easier filtering
    df = pd.DataFrame([dict(row._mapping) for row in data])
    
    # Extract Source Type (RSS vs YouTube)
    df['type'] = df['source'].apply(lambda x: "YouTube" if x.startswith("YouTube") else "RSS")
    
    type_filter = st.sidebar.multiselect("Content Type", options=df['type'].unique(), default=df['type'].unique())
    source_filter = st.sidebar.multiselect("Specific Sources", options=df['source'].unique(), default=df['source'].unique())

    # Apply filters
    filtered_df = df[(df['type'].isin(type_filter)) & (df['source'].isin(source_filter))]

    if st.sidebar.button("Refresh Pipeline"):
        st.info("Running pipeline... check terminal for progress.")
        # Note: In a real app, you'd trigger the pipeline script here
        st.rerun()

# --- Main Content ---
if not data or filtered_df.empty:
    st.info("No unread insights matching your filters. Run the pipeline!")
else:
    st.write(f"Showing {len(filtered_df)} insights.")
    
    for _, row in filtered_df.iterrows():
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"### [{row['title']}]({row['url']})")
                st.markdown(f"**Source:** {row['source']} | **Score:** <span class='score-badge'>{row['relevance_score']}/10</span>", unsafe_allow_html=True)
                st.write(row['summary'])
                st.caption(f"Published: {row['published_at'].strftime('%Y-%m-%d %H:%M') if pd.notnull(row['published_at']) else 'Unknown'}")
            
            with col2:
                st.write("") 
                st.write("")
                if st.button("Mark as Read", key=f"read_{row['id']}"):
                    mark_as_read(row['id'])
                    st.success("Done!")
                    st.rerun()
            
            st.divider()

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("InsightEngine v1.0 | Local Intelligence Engine")
