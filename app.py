import streamlit as st

from agents.orchestrator import orchestrate_merging_notes
from data.generate_summary import generate_summary
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
    get_funnel_id_input, display_bedroom_preference_selector,
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

# Get and validate client data
client_data = get_client_data(clients, funnel_id)

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

    summary_tab, details_tab, debug_tab = st.tabs(['AI Summary', 'Details', 'Debug'])

    with summary_tab:
        display_client_summary(client_name, summary_clean)

    with details_tab:

        with st.expander('Prospect Info'):
            display_prospect_info(merged_prospect)

        with st.expander('View Available Units'):
            bed_count_select, agg_select = create_unit_view_selectors(availability)
            display_unit_view(
                bed_count_select, agg_select, availability,
                average_view_full, minimum_view_full, maximum_view_full
            )

        with st.expander('Amenities Breakdown'):
            st.dataframe(amenities, use_container_width=True)

        with st.expander('Concessions Breakdown'):
            if len(concessions) > 0:
                st.dataframe(concessions, use_container_width=True)
            else:
                st.info("No active concessions found for the available properties.")

        with st.expander('Fees Breakdown'):
            st.dataframe(fees, use_container_width=True)

    with debug_tab:

        with st.expander('Messages to LLM'):
            st.write(messages)