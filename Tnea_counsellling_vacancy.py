import streamlit as st
import pandas as pd
import plotly.express as px

# Page Setup
st.set_page_config(page_title="TNEA Counselling Vacancy Dashboard", layout="wide")
st.title("🎓 TNEA Counselling Vacancy Dashboard")

# 🔰 Guide users to filter panel
st.info("📱 _Tip: Tap the top-left menu (>>) to open filters and narrow down your choices._")

# 📌 Choose Mode Header
st.markdown("### 📌 Choose your mode: General or 7.5% Reservation")

# Load CSVs
general_df = pd.read_csv("Cleaned_General_reservation.csv")
seven_df = pd.read_csv("cleaned_7.5_Reservation.csv")

# Melt category columns into long format
# Category columns used for filtering and totals
category_columns = ['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']

# Only renaming columns to standardize (no melting)
def preprocess(df):
    return df.rename(columns={
        'COLLEGE NAME': 'College Name',
        'BRANCH NAME': 'Branch Name',
        'District': 'District'
    })

general_df = preprocess(general_df)
seven_df = preprocess(seven_df)

# 🔘 Rectangular Toggle Buttons
colA, colB = st.columns(2)

if "reservation_type" not in st.session_state:
    st.session_state.reservation_type = "General Reservation"

with colA:
    if st.button("🟦 General Reservation"):
        st.session_state.reservation_type = "General Reservation"

with colB:
    if st.button("🟨 7.5% Reservation"):
        st.session_state.reservation_type = "7.5% Reservation"

reservation_type = st.session_state.reservation_type
df = general_df if reservation_type == "General Reservation" else seven_df

# 📂 Show current selection
st.markdown(f"🗂️ **Current Mode:** `{reservation_type}`")

# Sidebar Filters
st.sidebar.header("🔍 Filters")

# 1. District Filter
selected_districts = st.sidebar.multiselect("Select District", sorted(df['District'].unique()))

# 2. College Filter — dynamically show only colleges from selected districts
if selected_districts:
    filtered_colleges = df[df['District'].isin(selected_districts)]['College Name'].unique()
else:
    filtered_colleges = df['College Name'].unique()

selected_colleges = st.sidebar.multiselect("Select College Name", sorted(filtered_colleges))

# 3. Branch Filter
selected_branches = st.sidebar.multiselect("Select Branch Name", sorted(df['Branch Name'].unique()))

# 4. Reservation Category Filter (based on column names)
selected_categories = st.sidebar.multiselect("Select Reservation Category", sorted(category_columns))

# ✅ Apply Filters in sequence
filtered_df = df.copy()

if selected_districts:
    filtered_df = filtered_df[filtered_df['District'].isin(selected_districts)]
if selected_colleges:
    filtered_df = filtered_df[filtered_df['College Name'].isin(selected_colleges)]
if selected_branches:
    filtered_df = filtered_df[filtered_df['Branch Name'].isin(selected_branches)]
if selected_categories:
    mask = pd.Series(False, index=filtered_df.index)
    for cat in selected_categories:
        mask |= (filtered_df[cat] > 0)
    filtered_df = filtered_df[mask]

# 🎯 Total Available Seats
st.subheader(f"🎯 Total Available Seats: {int(filtered_df[category_columns].sum().sum())}")

# 📊 Bar Chart - District vs Category
st.markdown("### 📊 Total Seats by District & Category")

# Sum category columns by district
district_chart = (
    filtered_df.groupby('District')[category_columns]
    .sum()
    .reset_index()
    .melt(id_vars='District', var_name='Category', value_name='Available Seats')
)

fig1 = px.bar(
    district_chart,
    x='District',
    y='Available Seats',
    color='Category',
    title="Seats by District & Category",
    text='Available Seats'
)

fig1.update_traces(
    textposition='inside',
    textfont_size=10
)

st.plotly_chart(fig1, use_container_width=True)

# Pie Chart
st.markdown("### 🥧 Category-wise Seat Proportion")

category_pie = (
    filtered_df[category_columns]
    .sum()
    .reset_index()
    .rename(columns={0: 'Available Seats', 'index': 'Category'})
)

fig2 = px.pie(
    category_pie,
    names='Category',
    values='Available Seats',
    title="Category Share"
)

st.plotly_chart(fig2, use_container_width=True)

# 📋 Filtered Table
st.markdown("### 📋 Filtered Seat Availability Table")
st.dataframe(filtered_df, use_container_width=True)

# 📥 Download Buttons
st.markdown("### 📥 Download Filtered Data")
col_csv, col_excel = st.columns(2)
with col_csv:
    st.download_button("⬇️ Download CSV", filtered_df.to_csv(index=False), "vacancy_list_tnea.csv", "text/csv")

# 📘 Footer
st.markdown("---")
st.markdown(
    "📘 _Made with ❤️ for students and parents by [Abdul Malik](https://www.linkedin.com/in/abdulmalik2001/) — helping you choose better, faster._",
    unsafe_allow_html=True
)

