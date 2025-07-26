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

# 2. College Filter (based on selected district)
if selected_districts:
    filtered_df_district = df[df['District'].isin(selected_districts)]
    college_options = sorted(filtered_df_district['College Name'].unique())
else:
    filtered_df_district = df
    college_options = sorted(df['College Name'].unique())

selected_colleges = st.sidebar.multiselect("Select College Name", college_options)

# 3. Branch Filter (based on selected district + college)
if selected_colleges:
    filtered_df_college = filtered_df_district[filtered_df_district['College Name'].isin(selected_colleges)]
    branch_options = sorted(filtered_df_college['Branch Name'].unique())
else:
    filtered_df_college = filtered_df_district
    branch_options = sorted(filtered_df_district['Branch Name'].unique())

selected_branches = st.sidebar.multiselect("Select Branch Name", branch_options)

# 4. Reservation Category Filter (no dependency)
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
if selected_categories:
    total_seats = filtered_df[selected_categories].sum().sum()
else:
    total_seats = filtered_df[category_columns].sum().sum()

st.subheader(f"🎯 Total Available Seats: {int(total_seats)}")

# 📊 Bar Chart - District vs Category
st.markdown("### 📊 Total Seats by District & Category")

# Bar chart data prep
if selected_categories:
    bar_data = (
        filtered_df.groupby('District')[selected_categories]
        .sum()
        .reset_index()
    )
    bar_data = bar_data.melt(id_vars='District', var_name='Category', value_name='Available Seats')
else:
    bar_data = (
        filtered_df.groupby('District')[category_columns]
        .sum()
        .reset_index()
    )
    bar_data = bar_data.melt(id_vars='District', var_name='Category', value_name='Available Seats')

fig1 = px.bar(
    bar_data,
    x='District',
    y='Available Seats',
    color='Category',
    text='Available Seats',
    title="Seats by District & Category"
)
fig1.update_traces(textposition='inside', textfont_size=10)
st.plotly_chart(fig1, use_container_width=True)

# Pie Chart
st.markdown("### 🥧 Category-wise Seat Proportion")

if selected_categories:
    category_pie = (
        filtered_df[selected_categories]
        .sum()
        .reset_index()
        .rename(columns={'index': 'Category', 0: 'Available Seats'})
    )
else:
    category_pie = (
        filtered_df[category_columns]
        .sum()
        .reset_index()
        .rename(columns={'index': 'Category', 0: 'Available Seats'})
    )

category_pie.columns = ['Category', 'Available Seats']

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

