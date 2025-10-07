#  https://docs.streamlit.io/
# streamlit run student_dashboard_csv.py
# student_dashboard_csv.py
# ------------------------------------------
# Interactive Student Performance Dashboard
# Built with Streamlit + Plotly
# ------------------------------------------
# https://www.kdnuggets.com/7-python-libraries-every-analytics-engineer-should-know


import streamlit as st
import pandas as pd
import plotly.express as px
import os


# ------------------------------------------
# Page configuration
# ------------------------------------------
st.set_page_config(
    page_title="Student Performance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🎓 Student Performance Dashboard")
st.markdown("This dashboard visualizes student marks and performance across different disciplines and subjects.")

# ------------------------------------------
# Load Data
# ------------------------------------------
# data_path = os.path.join("data", "marks.csv")


BASE_DIR = os.path.dirname(__file__)
csv_path = os.path.join(BASE_DIR, "data", "marks.csv")

data_path = pd.read_csv(csv_path)

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

try:
    data = load_data(data_path)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

st.subheader("📄 Data Preview")
st.dataframe(data, use_container_width=True)

# ------------------------------------------
# Identify important columns
# ------------------------------------------
required_cols = {"Name", "Class", "Gender"}
exclude_cols = required_cols | {"Discipline"} if "Discipline" in data.columns else required_cols

# Detect numeric subject columns
numeric_cols = [
    col for col in data.columns
    if col not in exclude_cols and pd.api.types.is_numeric_dtype(data[col])
]

if not numeric_cols:
    st.warning("No numeric subject columns found. Please check your CSV data.")
    st.stop()

# ------------------------------------------
# Sidebar filters
# ------------------------------------------
st.sidebar.header("🔍 Filters")

# Discipline filter
if "Discipline" in data.columns:
    disciplines = sorted(data["Discipline"].dropna().unique())
    selected_discipline = st.sidebar.selectbox("Select Discipline", ["All"] + disciplines)
else:
    selected_discipline = "All"

if selected_discipline != "All":
    filtered_data = data[data["Discipline"] == selected_discipline]
else:
    filtered_data = data.copy()

# Gender filter
genders = sorted(filtered_data["Gender"].dropna().unique())
selected_gender = st.sidebar.multiselect("Select Gender(s)", genders, default=genders)

if selected_gender:
    filtered_data = filtered_data[filtered_data["Gender"].isin(selected_gender)]

# ------------------------------------------
# Summary Metrics
# ------------------------------------------
st.subheader("📊 Summary Statistics")

col1, col2, col3 = st.columns(3)
col1.metric("Total Students", len(filtered_data))
if "Discipline" in filtered_data.columns:
    col2.metric("Selected Discipline", selected_discipline)
else:
    col2.metric("Discipline", "N/A")

avg_score = filtered_data[numeric_cols].mean().mean()
col3.metric("Average Overall Marks", f"{avg_score:.2f}")

# ------------------------------------------
# Average Marks by Subject
# ------------------------------------------
st.subheader("📈 Average Marks by Subject")

subject_avg = (
    filtered_data.groupby("Gender")[numeric_cols].mean().reset_index()
    if "Gender" in filtered_data.columns else
    pd.DataFrame()
)

if not subject_avg.empty:
    fig1 = px.bar(
        subject_avg.melt(id_vars="Gender", var_name="Subject", value_name="Average Marks"),
        x="Subject",
        y="Average Marks",
        color="Gender",
        barmode="group",
        title="Average Marks by Subject and Gender",
    )
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("Not enough data to plot subject averages.")

# ------------------------------------------
# Subject Distribution
# ------------------------------------------
st.subheader("📊 Marks Distribution by Subject")

subject_for_dist = st.selectbox("Select Subject for Distribution", numeric_cols)

# Convert selected subject to numeric and clean
filtered_data[subject_for_dist] = pd.to_numeric(filtered_data[subject_for_dist], errors="coerce")
filtered_data = filtered_data.dropna(subset=[subject_for_dist])

if not filtered_data.empty:
    fig2 = px.histogram(
        filtered_data,
        x=subject_for_dist,
        nbins=10,
        color="Gender" if "Gender" in filtered_data.columns else None,
        barmode="overlay",
        title=f"Distribution of {subject_for_dist} Marks by Gender",
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning(f"No valid numeric data found for {subject_for_dist}.")

# ------------------------------------------
# Discipline-wise Average (if applicable)
# ------------------------------------------
if "Discipline" in data.columns:
    st.subheader("🏫 Average Marks by Discipline")

    disc_avg = data.groupby("Discipline")[numeric_cols].mean().reset_index()
    disc_avg["Overall Avg"] = disc_avg[numeric_cols].mean(axis=1)

    fig3 = px.bar(
        disc_avg,
        x="Discipline",
        y="Overall Avg",
        title="Average Performance by Discipline",
        color="Discipline",
    )
    st.plotly_chart(fig3, use_container_width=True)

# ------------------------------------------
# Footer
# ------------------------------------------
st.markdown("---")
st.markdown("Developed with ❤️ using **Streamlit** and **Plotly**.")
