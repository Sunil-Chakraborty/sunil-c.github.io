# ----------------------------------------------------
# 🎓 Interactive Student Intake Dashboard (Read-Only UI)
# Streamlit + Altair | Mobile-Responsive | Clean Display
# ----------------------------------------------------
# Run locally:  streamlit run Student_DB.py
# ----------------------------------------------------
# Live app: https://sunilc-intake.streamlit.app/
# ----------------------------------------------------

import streamlit as st
import pandas as pd
import altair as alt
import os

# --- Configuration & Read-Only Style ---
st.set_page_config(
    page_title="Intake Gap Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide all Streamlit Cloud UI (menu, manage app, footer)
hide_streamlit_style = """
<style>
/* Hide Streamlit main menu (top right corner) */
#MainMenu {visibility: hidden;}

/* Hide "Manage App" and Cloud controls (bottom right corner) */
button[kind="header"] {display: none !important;}
a[data-testid="stToolbarActions"] {display: none !important;}

/* Hide Streamlit footer */
footer {visibility: hidden;}

/* Hide "View fullscreen" and similar chart tools */
[data-testid="StyledFullScreenButton"] {display: none !important;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- Data Loading and Preparation ---
@st.cache_data
def load_data(file_path):
    """Loads and preprocesses the intake gap data."""
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        st.stop()

    # Melt the data for Gap columns (K-M)
    melted_df = df.melt(
        id_vars=['Prog_Tag', 'Programme Name', 'Department', 'Faculty'],
        value_vars=['Gap 2022-23', 'Gap 2023-24', 'Gap 2024-25'],
        var_name='Year',
        value_name='Gap'
    )

    # Rename columns for cleaner display
    melted_df.columns = ['Program Tag', 'Program Name', 'Department', 'Faculty', 'Year', 'Gap']

    # Convert 'Year' to categorical for correct plotting order
    melted_df['Year'] = pd.Categorical(
        melted_df['Year'],
        categories=['Gap 2022-23', 'Gap 2023-24', 'Gap 2024-25'],
        ordered=True
    )
    
    return melted_df


# --- Load Data ---
BASE_DIR = os.path.dirname(__file__)
data_path = os.path.join(BASE_DIR, "data", "intake_gaps.csv")
data = load_data(data_path)


# --- Streamlit Layout ---
st.title('📊 Intake Gap Analysis Dashboard')

# --- Sidebar for Drill-Down Filters ---
st.sidebar.header('Drill-Down Filters')

# Get unique values for filters
all_program_tags = ['All'] + sorted(data['Program Tag'].unique().tolist())
all_departments = ['All'] + sorted(data['Department'].unique().tolist())
all_faculties = ['All'] + sorted(data['Faculty'].unique().tolist())
all_program_names = ['All'] + sorted(data['Program Name'].unique().tolist())
all_gap_years = sorted(data['Year'].unique().tolist())

# Filter widgets
selected_tag = st.sidebar.selectbox('Select Program Tag (Col A)', all_program_tags)
selected_department = st.sidebar.selectbox('Select Department (Col C)', all_departments)
selected_faculty = st.sidebar.selectbox('Select Faculty (Col D)', all_faculties)
selected_program = st.sidebar.selectbox('Select Program Name (Col B)', all_program_names)
selected_years = st.sidebar.multiselect(
    'Select Gap Years (Cols K-M)',
    options=all_gap_years,
    default=all_gap_years
)

# --- Filtering Logic ---
filtered_data = data.copy()

if selected_tag != 'All':
    filtered_data = filtered_data[filtered_data['Program Tag'] == selected_tag]

if selected_department != 'All':
    filtered_data = filtered_data[filtered_data['Department'] == selected_department]

if selected_faculty != 'All':
    filtered_data = filtered_data[filtered_data['Faculty'] == selected_faculty]

if selected_program != 'All':
    filtered_data = filtered_data[filtered_data['Program Name'] == selected_program]

if selected_years:
    filtered_data = filtered_data[filtered_data['Year'].isin(selected_years)]
else:
    st.warning("Please select at least one Gap Year to display data.")
    filtered_data = pd.DataFrame()


# --- Visualization ---
st.header('Intake Gap Over Years (2022-25)')

if filtered_data.empty:
    if selected_years:
        st.warning("No data matches the current filter selections.")
else:
    # Aggregate and prepare chart data
    chart_data = filtered_data.groupby(['Program Tag', 'Year'], observed=True)['Gap'].sum().reset_index()

    # Create Altair grouped bar chart
    chart = (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X('Program Tag', axis=None),
            y=alt.Y('sum(Gap)', title='Intake Gap (Sanctioned - Actual)'),
            color=alt.Color('Year', title='Academic Year'),
            column=alt.Column('Year', title=''),
            tooltip=['Program Tag', 'Year', alt.Tooltip('sum(Gap)', title='Total Gap')],
        )
        .properties(title='Gap by Program Tag and Year')
        .interactive()
    )

    st.altair_chart(chart, use_container_width=True)

    # Display filtered table
    st.subheader('Filtered Data Table')
    st.dataframe(filtered_data, use_container_width=True)


# --- Sidebar Info ---
st.sidebar.markdown('---')
st.sidebar.info('Gap = Sanctioned Intake − Actual Intake')
st.sidebar.info('**Positive Gap:** actual intake was less than sanctioned.')
st.sidebar.info('**Negative Gap:** actual intake was more than sanctioned (over-intake).')
