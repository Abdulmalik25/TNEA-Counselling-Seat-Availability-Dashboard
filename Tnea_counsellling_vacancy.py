import streamlit as st
import pandas as pd
import plotly.express as px

# Page Setup
st.set_page_config(page_title="TNEA Counselling Vacancy Dashboard", layout="wide")
st.title("🎓 TNEA Counselling Vacancy Dashboard")

# Load CSVs
general_df = pd.read_csv("Cleaned_General_reservation.csv")
seven_df = pd.read_csv("cleaned_7.5_Reservation.csv")

# Melt category columns into long format
category_columns = ['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']

def preprocess(df):
    df = df.rename(columns={
        'COLLEGE NAME': 'College Name',
        'BRANCH NAME': 'Branch Name',
        'District': 'District'
    })
    melted = df.melt(
        id_vars=['College Name', 'Branch Name', 'District', 'Total_Seats'],
        value_vars=category_columns,
        var_name='Category',
        value_name='Available Seats'
    )
    return melted

general_df = preprocess(general_df)
seven_df = preprocess(seven_df)

# Toggle Button
# Create two rectangular toggle buttons side by side
colA, colB = st.columns(2)

# Initialize session state
if "reservation_type" not in st.session_state:
    st.session_state.reservation_type = "General Reservation"

with colA:
    if st.button("🟦 General Reservation"):
        st.session_state.reservation_type = "General Reservation"

with colB:
    if st.button("🟨 7.5% Reservation"):
        st.session_state.reservation_type = "7.5% Reservation"

# Use session state to select dataset
reservation_type = st.session_state.reservation_type
df = general_df if reservation_type == "General Reservation" else seven_df

# Show which type is active
st.markdown(f"**Current Mode:** `{reservation_type}`")

# Sidebar filters
st.sidebar.header("🔍 Filters")
with st.sidebar:
    selected_districts = st.multiselect("Select District", sorted(df['District'].unique()))
    selected_colleges = st.multiselect("Select College Name", sorted(df['College Name'].unique()))
    selected_branches = st.multiselect("Select Branch Name", sorted(df['Branch Name'].unique()))
    selected_categories = st.multiselect("Select Reservation Category", sorted(df['Category'].unique()))

# Conditional filter logic
filtered_df = df.copy()
if selected_districts:
    filtered_df = filtered_df[filtered_df['District'].isin(selected_districts)]
if selected_colleges:
    filtered_df = filtered_df[filtered_df['College Name'].isin(selected_colleges)]
if selected_branches:
    filtered_df = filtered_df[filtered_df['Branch Name'].isin(selected_branches)]
if selected_categories:
    filtered_df = filtered_df[filtered_df['Category'].isin(selected_categories)]

# Total available seats
st.subheader(f"🎯 Total Available Seats: {int(filtered_df['Available Seats'].sum())}")



# Total Seats per District (Stacked)
st.markdown("### 📊 Total Seats per District (Stacked by Category)")
district_chart = filtered_df.groupby(['District', 'Category'])['Available Seats'].sum().reset_index()

fig1 = px.bar(
    district_chart,
    x='District',
    y='Available Seats',
    color='Category',
    title="Seats by District & Category",
    text='Available Seats'  # enable text labels
)

# Make the text smaller and inside bars
fig1.update_traces(
    textposition='inside',
    textfont_size=10
)

st.plotly_chart(fig1, use_container_width=True)

# Pie Chart
st.markdown("### 🥧 Category-wise Seat Proportion")
category_pie = filtered_df.groupby('Category')['Available Seats'].sum().reset_index()
fig2 = px.pie(category_pie, names='Category', values='Available Seats', title="Category Share")
st.plotly_chart(fig2, use_container_width=True)

# Heatmap
st.markdown("### 🌡️ Heatmap: Seats by District & Category")
heatmap_data = filtered_df.groupby(['District', 'Category'])['Available Seats'].sum().reset_index()
pivot_heatmap = heatmap_data.pivot(index='District', columns='Category', values='Available Seats').fillna(0)
fig3 = px.imshow(pivot_heatmap, text_auto=True, aspect="auto", title="Heatmap of Available Seats")
st.plotly_chart(fig3, use_container_width=True)

# Final Filtered Table
st.markdown("### 📋 Filtered Seat Availability Table")
st.dataframe(filtered_df, use_container_width=True)

# Download Buttons
st.markdown("### 📥 Download Filtered Data")
col_csv, col_excel = st.columns(2)
with col_csv:
    st.download_button("⬇️ Download CSV", filtered_df.to_csv(index=False), "filtered_tnea.csv", "text/csv")

# Footer
st.markdown("---")
st.markdown(
    "📘 _Made with ❤️ for students and parents by [Abdul Malik](https://www.linkedin.com/in/abdulmalik2001/) — helping you choose better, faster._",
    unsafe_allow_html=True
)