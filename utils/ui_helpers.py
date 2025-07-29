"""
UI helper functions for Streamlit interface.
"""

import streamlit as st
from constants import SIDEBAR_WIDTH, BEDROOM_DISPLAY_NAMES, AGGREGATION_OPTIONS


def setup_sidebar_styling():
    """Apply custom CSS styling to sidebar."""
    st.markdown(f"""
        <style>
            [data-testid="stSidebar"] {{
                width: {SIDEBAR_WIDTH}px;
                background-color: #183c7d !important;
                border-right: 1px solid #e0e0e0;
            }}
            
            /* All sidebar text elements */
            [data-testid="stSidebar"] * {{
                color: white !important;
            }}
            
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
                color: white !important;
                font-weight: 600 !important;
            }}
            
            [data-testid="stSidebar"] .stMarkdown h1,
            [data-testid="stSidebar"] .stMarkdown h2,
            [data-testid="stSidebar"] .stMarkdown h3,
            [data-testid="stSidebar"] h1,
            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3 {{
                color: white !important;
                font-weight: 600 !important;
            }}
            
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] .stSelectbox label,
            [data-testid="stSidebar"] .stTextInput label,
            [data-testid="stSidebar"] .stMultiSelect label {{
                color: white !important;
                font-weight: 500 !important;
            }}
            
            /* Expander styling */
            [data-testid="stSidebar"] .streamlit-expanderHeader,
            [data-testid="stSidebar"] details summary {{
                color: white !important;
                background-color: rgba(255, 255, 255, 0.1) !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                border-radius: 6px !important;
                font-weight: 600 !important;
            }}
            
            [data-testid="stSidebar"] .streamlit-expanderHeader:hover,
            [data-testid="stSidebar"] details summary:hover {{
                background-color: rgba(255, 255, 255, 0.2) !important;
            }}
            
            [data-testid="stSidebar"] .streamlit-expanderContent *,
            [data-testid="stSidebar"] details div * {{
                color: #333 !important;
            }}
            
            /* Button styling */
            [data-testid="stSidebar"] .stButton > button,
            [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {{
                background-color: #183c7d !important;
                color: white !important;
                border: none !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                transition: all 0.2s ease !important;
            }}
            
            [data-testid="stSidebar"] .stButton > button:hover,
            [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {{
                background-color: #1e4a8c !important;
                transform: translateY(-1px) !important;
            }}
            
            [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] p {{
                color: white !important;
            }}
            
            /* Input styling */
            [data-testid="stSidebar"] .stTextInput > div > div > input {{
                background-color: rgba(255, 255, 255, 0.9) !important;
                color: #333 !important;
                border: 1px solid rgba(255, 255, 255, 0.3) !important;
                border-radius: 6px !important;
            }}
            
            [data-testid="stSidebar"] .stMultiSelect > div > div {{
                background-color: rgba(255, 255, 255, 0.9) !important;
                border-radius: 6px !important;
            }}
            
            [data-testid="stSidebar"] .stSelectbox > div > div {{
                background-color: rgba(255, 255, 255, 0.9) !important;
                border-radius: 6px !important;
            }}
            
            /* Warning styling in sidebar */
            [data-testid="stSidebar"] .stAlert {{
                background-color: rgba(255, 193, 7, 0.1) !important;
                border-left: 4px solid #ffc107 !important;
                border-radius: 6px !important;
                color: #fff !important;
            }}
            
            [data-testid="stSidebar"] .stAlert [data-testid="stMarkdownContainer"] {{
                color: #fff !important;
            }}
            
            [data-testid="stSidebar"] .stAlert p {{
                color: #fff !important;
                font-weight: 500 !important;
            }}
        </style>
    """, unsafe_allow_html=True)


def setup_modern_app_styling():
    """Apply modern styling to the entire app."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            .stApp {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }}
            
            /* Tab styling */
            .stTabs [data-baseweb="tab-list"] {{
                gap: 8px;
                background-color: #f8f9fa;
                border-radius: 12px;
                padding: 4px;
                margin-bottom: 20px;
            }}

            .stTabs [data-baseweb="tab"] {{
                height: 40px;
                padding: 0px 24px;
                background-color: transparent;
                border-radius: 8px;
                color: #6c757d;
                font-weight: 500;
                border: none;
                transition: all 0.2s ease;
            }}

            .stTabs [data-baseweb="tab"][aria-selected="true"] {{
                background-color: white;
                color: #183c7d;
                font-weight: 600;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            
            /* Expander styling */
            .streamlit-expanderHeader {{
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                font-weight: 600;
                color: #495057;
                padding: 12px 16px;
                transition: all 0.2s ease;
            }}
            
            .streamlit-expanderHeader:hover {{
                background-color: #e9ecef;
                border-color: #dee2e6;
            }}
            
            .streamlit-expanderContent {{
                border: 1px solid #e9ecef;
                border-top: none;
                border-radius: 0 0 8px 8px;
                padding: 16px;
                background-color: white;
            }}
            
            /* Dataframe styling */
            .stDataFrame {{
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }}
            
            /* Selectbox styling */
            .stSelectbox > div > div {{
                border-radius: 8px;
                border: 1px solid #e9ecef;
                transition: all 0.2s ease;
            }}
            
            .stSelectbox > div > div:focus-within {{
                border-color: #183c7d;
                box-shadow: 0 0 0 2px rgba(24, 60, 125, 0.1);
            }}
            
            /* Spinner styling */
            .stSpinner > div {{
                border-top-color: #183c7d !important;
            }}
            
            /* Alert styling */
            .stAlert[data-baseweb="notification"] {{
                border-radius: 8px;
                border-left: 4px solid #ffc107;
            }}
            
            .stAlert[kind="error"] {{
                background-color: #f8d7da;
                border-left: 4px solid #dc3545;
                color: #721c24;
            }}
            
            .stAlert[kind="warning"] {{
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                color: #856404;
            }}
            
            .stAlert[kind="success"] {{
                background-color: #d1edff;
                border-left: 4px solid #0066cc;
                color: #004085;
            }}
        </style>
    """, unsafe_allow_html=True)


def display_example_clients(example_clients):
    """Display example clients in sidebar expander."""
    with st.sidebar.expander('Example GC IDs'):
        st.write(example_clients)


def get_funnel_id_input():
    """Get funnel ID input from sidebar."""
    return st.sidebar.text_input(label='Input GC ID')


def display_bedroom_preference_selector(bed_preferences_default=None):
    """Display bedroom preference multiselect widget."""
    if bed_preferences_default is None:
        bed_preferences_default = []
    
    return st.sidebar.multiselect(
        label='Select Bed Preferences',
        options=[0, 1, 2, 3],
        format_func=lambda x: BEDROOM_DISPLAY_NAMES[x],
        default=bed_preferences_default
    )


def get_submit_button():
    """Display submit button in sidebar."""
    return st.sidebar.button("Submit")


def display_client_summary(client_name, summary_clean):
    """Display client summary in formatted container."""
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 28px;
            border-radius: 12px;
            border: 1px solid #e9ecef;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            margin-bottom: 24px;
        ">
            <h2 style="
                color: #183c7d;
                font-weight: 700;
                margin-bottom: 20px;
                font-size: 1.75rem;
                border-bottom: 2px solid #183c7d;
                padding-bottom: 8px;
            ">{client_name}</h2>
            <div style="
                line-height: 1.6;
                color: #495057;
                font-size: 0.95rem;
            ">
                {summary_clean}
            </div>
        </div>
    """, unsafe_allow_html=True)


def create_unit_view_selectors(availability):
    """Create bed count and aggregation selectors for unit view."""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        bed_count_select = st.selectbox(
            'Select Bed Count',
            options=sorted(availability['beds'].unique()),
        )
    
    with col2:
        agg_select = st.selectbox(
            'Select Rollup',
            options=AGGREGATION_OPTIONS
        )
    
    return bed_count_select, agg_select


def display_unit_view(bed_count_select, agg_select, availability, average_view_full, minimum_view_full, maximum_view_full):
    """Display unit view based on selections."""
    # Filter views by bed count
    individual_view = availability[availability['beds'] == int(bed_count_select)].drop(columns='hellodata_id')
    avg_view = average_view_full[average_view_full['beds'] == int(bed_count_select)]
    min_view = minimum_view_full[minimum_view_full['beds'] == int(bed_count_select)]
    max_view = maximum_view_full[maximum_view_full['beds'] == int(bed_count_select)]
    
    # Display appropriate view
    if agg_select == 'Individual':
        st.dataframe(individual_view)
    elif agg_select == 'Property Average':
        st.dataframe(avg_view)
    elif agg_select == 'Property Maximum':
        st.dataframe(max_view)
    else:  # Property Minimum
        st.dataframe(min_view)