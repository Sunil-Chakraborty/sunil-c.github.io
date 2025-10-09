# ----------------------------------------------------
# 🎓 Interactive Student Performance Dashboard
# Streamlit + Plotly | Mobile-Responsive | Dark/Light Mode
# ----------------------------------------------------
# Run locally:  streamlit run dashboard.py
# ----------------------------------------------------

import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------
st.set_page_config(
    page_title="Student Performance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# ------------------------------------------
# CSS for Clean UI + Mobile Responsiveness
# ------------------------------------------
st.markdown(
    """
    <style>
    /* Hide Streamlit header, menu, and footer */
    header, .css-18ni7ap.e8zbici2 {visibility: hidden;}
    #MainMenu, footer {visibility: hidden;}

    /* Responsive container */
    .block-container {
        padding-top: 1rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 100% !important;
    }

    /* Mobile-friendly text scaling */
    @media (max-width: 768px) {
        .stMarkdown, .stDataFrame, .stPlotlyChart {
            font-size: 15px !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: 22px !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 13px !important;
        }
        h1, h2, h3, h4 {
            font-size: 20px !important;
        }
    }

    /* Metric Card Styling (Dark & Light Base) */
    div[data-testid="stMetric"] {
        border-radius: 12px;
        padding: 15px 20px;
        margin: 5px;
        text-align: center;
        transition: all 0.3s ease;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------------------------
# THEME TOGGLE
# ------------------------------------------
st.sidebar.header("🎨 Theme")
theme_option = st.sidebar.radio("Select Theme", ["Light", "Dark"])

if theme_option == "Dark":
    st.markdown(
        """
        <style>
        /* Base dark theme */
        body, .stApp {
            background-color: #0F0F0F;
            color: #FFFFFF;
        }

        .stButton>button {
            background-color: #333333;
            color: #FFFFFF;
            border-radius: 10px;
        }

        /* --- Metric Card Container --- */
        div[data-testid="stMetric"] {
            background-color: #1a1a1a !important;
            border-radius: 14px;
            padding: 18px 10px;
            margin: 8px;
            border: 1px solid #2c2c2c;
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.05);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center !important;
        }

        /* --- Metric Label --- */
        div[data-testid="stMetric"] > div:nth-child(1) {
            color: #FFB347 !important;   /* amber label */
            font-weight: 600 !important;
            font-size: 14px !important;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            text-align: center !important;
            margin-bottom: 5px;
        }

        /* --- Metric Value --- */
        div[data-testid="stMetricValue"] {
            color: #00E0FF !important;   /* bright cyan value */
            font-size: 28px !important;
            font-weight: 700 !important;
            text-align: center !important;
        }

        /* --- Subheader --- */
        h3, .stSubheader, [data-testid="stMarkdownContainer"] h3 {
            color: #FFD166 !important;
        }

        /* --- Responsive: mobile view --- */
        @media (max-width: 768px) {
            div[data-testid="stMetric"] {
                padding: 10px;
                margin: 4px 0;
            }
            div[data-testid="stMetricValue"] {
                font-size: 24px !important;
            }
            div[data-testid="stMetric"] > div:nth-child(1) {
                font-size: 13px !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

else:
    st.markdown(
        """
        <style>
        /* Light Mode Metric Styling */
        /* --- Metric Label --- */
        div[data-testid="stMetric"] > div:nth-child(1) {
            color: #FFB347 !important;   /* amber label */
            font-weight: 600 !important;
            font-size: 14px !important;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            text-align: center !important;
            margin-bottom: 5px;
        }
        div[data-testid="stMetricValue"] {
            color: #007BFF !important;
            font-weight: 700;
        }
        div[data-testid="stMetricLabel"] {
            color: #555555 !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# ------------------------------------------
# TITLE
# ------------------------------------------
st.title("🎓 Student Performance Dashboard")
st.markdown("A responsive, mobile-friendly dashboard to visualize student performance.")

# ------------------------------------------
# LOAD DATA
# ------------------------------------------
BASE_DIR = os.path.dirname(__file__)
data_path = os.path.join(BASE_DIR, "data", "marks.csv")

@st.cache_data
def load_data(path):
    return pd.read_csv(path)

try:
    data = load_data(data_path)
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# Allow upload
st.sidebar.header("📂 Upload Data (Optional)")
uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])
if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)
    st.success(f"✅ Loaded file: {uploaded_file.name}")

# ------------------------------------------
# FILTERS
# ------------------------------------------
with st.sidebar.expander("🔍 Filters", expanded=True):
    if "Discipline" in data.columns:
        disciplines = sorted(data["Discipline"].dropna().unique())
        selected_discipline = st.selectbox("Select Discipline", ["All"] + disciplines)
    else:
        selected_discipline = "All"

    filtered_data = data.copy()
    if selected_discipline != "All":
        filtered_data = filtered_data[filtered_data["Discipline"] == selected_discipline]

    if "Gender" in filtered_data.columns:
        genders = sorted(filtered_data["Gender"].dropna().unique())
        selected_gender = st.multiselect("Select Gender(s)", genders, default=genders)
        if selected_gender:
            filtered_data = filtered_data[filtered_data["Gender"].isin(selected_gender)]

# ------------------------------------------
# SUMMARY METRICS
# ------------------------------------------
st.subheader("📊 Summary Statistics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Students", len(filtered_data))
col2.metric("Selected Discipline", selected_discipline if "Discipline" in filtered_data.columns else "N/A")
numeric_cols = [c for c in data.columns if pd.api.types.is_numeric_dtype(data[c])]
avg_score = filtered_data[numeric_cols].mean().mean() if numeric_cols else 0
col3.metric("Average Overall Marks", f"{avg_score:.2f}")

# ------------------------------------------
# DATA PREVIEW
# ------------------------------------------
st.subheader("📄 Data Preview")
st.dataframe(filtered_data, use_container_width=True, height=400)

# ------------------------------------------
# AVERAGE MARKS BY SUBJECT
# ------------------------------------------
st.subheader("📈 Average Marks by Subject")
if "Gender" in filtered_data.columns:
    subject_avg = filtered_data.groupby("Gender")[numeric_cols].mean().reset_index()
    fig1 = px.bar(
        subject_avg.melt(id_vars="Gender", var_name="Subject", value_name="Average Marks"),
        x="Subject", y="Average Marks", color="Gender",
        barmode="group", title="Average Marks by Subject and Gender",
    )
    if theme_option == "Dark":
        fig1.update_layout(template="plotly_dark", paper_bgcolor="#111", plot_bgcolor="#111")
    st.plotly_chart(fig1, use_container_width=True)

# ------------------------------------------
# SUBJECT DISTRIBUTION
# ------------------------------------------
st.subheader("📊 Marks Distribution by Subject")
subject_for_dist = st.selectbox("Select Subject", numeric_cols)
filtered_data[subject_for_dist] = pd.to_numeric(filtered_data[subject_for_dist], errors="coerce")
filtered_data = filtered_data.dropna(subset=[subject_for_dist])
if not filtered_data.empty:
    fig2 = px.histogram(
        filtered_data, x=subject_for_dist, nbins=10,
        color="Gender" if "Gender" in filtered_data.columns else None,
        barmode="overlay", title=f"Distribution of {subject_for_dist} Marks by Gender",
    )
    if theme_option == "Dark":
        fig2.update_layout(template="plotly_dark", paper_bgcolor="#111", plot_bgcolor="#111")
    st.plotly_chart(fig2, use_container_width=True)

# ------------------------------------------
# DISCIPLINE-WISE AVERAGE
# ------------------------------------------
if "Discipline" in data.columns:
    st.subheader("🏫 Average Marks by Discipline")
    disc_avg = data.groupby("Discipline")[numeric_cols].mean().reset_index()
    disc_avg["Overall Avg"] = disc_avg[numeric_cols].mean(axis=1)
    fig3 = px.bar(
        disc_avg, x="Discipline", y="Overall Avg",
        color="Discipline", title="Average Performance by Discipline",
    )
    if theme_option == "Dark":
        fig3.update_layout(template="plotly_dark", paper_bgcolor="#111", plot_bgcolor="#111")
    st.plotly_chart(fig3, use_container_width=True)

# ------------------------------------------
# FOOTER
# ------------------------------------------
st.markdown("---")
st.caption("Developed with ❤️ using Streamlit + Plotly | Mobile-optimized for viewing on any device.")
