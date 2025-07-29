import streamlit as st

from agents.orchestrator import orchestrate_merging_notes
from data.generate_summary import generate_summary, style_internal_assets
from services.data_loader import load_all_data
from services.client_service import (
    get_client_data, merge_client_with_assignments, 
    has_bedroom_preferences, set_bedroom_preferences,
    prepare_example_clients
)
from services.validation_service import (
    validate_funnel_id, validate_client_exists, 
    validate_client_active, handle_validation_error,
    safe_get_prospect_data
)
from utils.ui_helpers import (
    setup_sidebar_styling, setup_modern_app_styling, display_example_clients,
    get_funnel_id_input, get_additional_notes_input, display_bedroom_preference_selector,
    get_submit_button, display_client_summary, display_prospect_info,
    create_unit_view_selectors, display_unit_view
)

# Setup UI styling
setup_sidebar_styling()
setup_modern_app_styling()

# Load all data
data = load_all_data()
clients = data['clients']
group_assignment = data['group_assignment']
internal_ref = data['internal_ref']
master_complist = data['master_complist']
concessions_history = data['concessions_history']
comp_details = data['comp_details']

st.sidebar.header('Leasing Edge Tool')

# Prepare and display example clients
example_clients = prepare_example_clients(clients, group_assignment, internal_ref)
display_example_clients(example_clients)

# Get and validate funnel ID input
funnel_id_input = get_funnel_id_input()

if not funnel_id_input:
    st.stop()

is_valid, funnel_id, error_msg = validate_funnel_id(funnel_id_input)
if not is_valid:
    handle_validation_error(error_msg)

additional_notes = get_additional_notes_input()

# Get and validate client data
client_data = get_client_data(clients, funnel_id)

client_data['notes'] += additional_notes

is_valid, error_msg = validate_client_exists(client_data)
if not is_valid:
    handle_validation_error(error_msg)

# Merge client data with assignments
merged_client_data = merge_client_with_assignments(client_data, group_assignment, internal_ref)

is_valid, error_msg = validate_client_active(merged_client_data)
if not is_valid:
    handle_validation_error(error_msg)

prospect = safe_get_prospect_data(merged_client_data)

# Handle bedroom preferences
if not has_bedroom_preferences(prospect):
    st.sidebar.warning('Prospect has no listed bedroom preferences')
    bed_preferences = display_bedroom_preference_selector()
    prospect = set_bedroom_preferences(prospect, bed_preferences)

submit = get_submit_button()

if submit:
    tool_args, merged_prospect = orchestrate_merging_notes(prospect)

    hellodata_property = merged_prospect['hellodata_property']
    hellodata_id = merged_prospect['hellodata_id']
    client_name = merged_prospect['client_full_name']

    messages, average_view_full, minimum_view_full, maximum_view_full, summary_clean, availability, amenities, fees, concessions = \
        generate_summary(hellodata_property, hellodata_id, merged_prospect, concessions_history, comp_details)
        
    if messages is None:
        st.stop()

    # Store data in session state for navigation
    st.session_state.data_loaded = True
    st.session_state.client_name = client_name
    st.session_state.summary_clean = summary_clean
    st.session_state.merged_prospect = merged_prospect
    st.session_state.availability = availability
    st.session_state.average_view_full = average_view_full
    st.session_state.minimum_view_full = minimum_view_full
    st.session_state.maximum_view_full = maximum_view_full
    st.session_state.amenities = amenities
    st.session_state.fees = fees
    st.session_state.concessions = concessions
    st.session_state.messages = messages

# Check if data is loaded before showing navigation
if st.session_state.get('data_loaded', False):
    
    # Define navigation page functions
    def ai_summary_page():
        display_client_summary(st.session_state.client_name, st.session_state.summary_clean)
    
    def prospect_info_page():
        display_prospect_info(st.session_state.merged_prospect)
    
    def view_availability_page():
        bed_count_select, agg_select = create_unit_view_selectors(st.session_state.availability)
        display_unit_view(
            bed_count_select, agg_select, st.session_state.availability,
            st.session_state.average_view_full, st.session_state.minimum_view_full, st.session_state.maximum_view_full
        )
    
    def amenities_page():
        st.dataframe(style_internal_assets(st.session_state.amenities), use_container_width=True)
    
    def concessions_page():
        if len(st.session_state.concessions) > 0:
            st.dataframe(style_internal_assets(st.session_state.concessions), use_container_width=True)
        else:
            st.info("No active concessions found for the available properties.")
    
    def fees_page():
        st.dataframe(style_internal_assets(st.session_state.fees), use_container_width=True)
    
    def debug_page():
        st.write(st.session_state.messages)

    # Create page objects
    ai_summary = st.Page(ai_summary_page, title="AI Summary")
    prospect_info = st.Page(prospect_info_page, title="Prospect Info")
    view_availability = st.Page(view_availability_page, title="View Availability")
    amenities = st.Page(amenities_page, title="Amenities Breakdown")
    concessions = st.Page(concessions_page, title="Concessions Breakdown")
    fees = st.Page(fees_page, title="Fees Breakdown")
    debug = st.Page(debug_page, title="Debug")

    # Create navigation
    pg = st.navigation({
        "Main": [ai_summary],
        "Details": [prospect_info, view_availability, amenities, concessions, fees],
        "Debug": [debug]
    }, position="top")
    
    pg.run()