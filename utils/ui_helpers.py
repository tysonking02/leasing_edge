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
        <div style="background-color: #f5f5f5; padding: 20px; border-radius: 6px;">
            <h2>{client_name}</h2>
            {summary_clean}
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<br>', unsafe_allow_html=True)


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