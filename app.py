import pandas as pd
import streamlit as st
import re

from agents.orchestrator import orchestrate_merging_notes, orchestrate_rollup_summary
from data.generate_summary import generate_summary

st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            width: 350px;
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_clients():
    return pd.read_csv(
        "data/processed/export_clients.csv", 
        usecols=[
            'client_id', 'client_email', 'client_full_name', 'client_status', 
            'laundry_preference', 'outdoor_space_preference', 'parking_preference', 
            'pet_preference', 'notes',
            'studio_preference', 'onebed_preference', 'twobed_preference', 
            'threebed_preference', 'fourbed_preference'
        ], 
        dtype={
            'client_id': int, 'client_email': str, 'client_full_name': str, 'client_status': str, 'laundry_preference': str, 
            'outdoor_space_preference': str, 'parking_preference': str, 'pet_preference': str,
            'studio_preference': bool, 'onebed_preference': bool, 'twobed_preference': bool, 'threebed_preference': bool, 'fourbed_preference': bool, 
            'notes': str
        }
    )

@st.cache_data
def load_group_assignment():
    return pd.read_csv(
        "data/processed/export_group_assignment.csv",
        usecols=['clientid', 'pms_community_id'],
        dtype={'clientid': 'Int64', 'pms_community_id': 'Int64'}
    )

@st.cache_data
def load_internal_ref():
    return pd.read_csv(
        "data/processed/hellodata_internal_ref.csv"
    )

@st.cache_data
def load_master_complist():
    return pd.read_csv(
        "data/processed/master_complist.csv"
    )

@st.cache_data
def load_concessions():
    all_concessions = pd.read_csv(
        "data/raw/concessions_history.csv",
        usecols=['property_id', 'from_date', 'to_date', 'concession_text']
    )

    return all_concessions[pd.to_datetime(all_concessions['to_date']) >= pd.Timestamp.now() - pd.Timedelta(days=7)]

@st.cache_data
def load_comp_details():
    return pd.read_csv(
        "data/processed/comp_details.csv",
        usecols=['asset', 'hellodata_id', 'year_built', 'cats_monthly_rent', 'cats_one_time_fee', 'cats_deposit', 'dogs_monthly_rent', 'dogs_one_time_fee', 'dogs_deposit',
                 'admin_fee', 'amenity_fee', 'application_fee', 'storage_fee', 'property_quality', 'building_amenities', 'unit_amenities']
    )

clients = load_clients()
group_assignment = load_group_assignment()
internal_ref = load_internal_ref()
master_complist = load_master_complist()
concessions_history = load_concessions()
comp_details = load_comp_details()

st.sidebar.header('Leasing Edge Tool')

# with st.sidebar.expander('Find GC IDs'):
#     property_select = st.selectbox('Select Property', options=sorted(internal_ref['hellodata_property'].unique()))

example_clients = pd.merge(clients, group_assignment, left_on = 'client_id', right_on = 'clientid')
example_clients = pd.merge(example_clients, internal_ref, left_on = 'pms_community_id', right_on = 'oslPropertyID')
example_clients = example_clients[['client_id', 'client_full_name', 'ParentAssetName']]

with st.sidebar.expander('Example GC IDs'):
    st.write(example_clients.sort_values('client_id', ascending=False).reset_index(drop=True))

funnel_id = st.sidebar.text_input(label='Input GC ID')

submit = st.sidebar.button("Submit")

if funnel_id == '':
    st.stop()

funnel_id = int(funnel_id)

client_data = clients[clients['client_id'] == funnel_id]

if len(client_data) == 0:
    st.sidebar.warning('Invalid GC ID')
    st.stop()

client_data = pd.merge(client_data, group_assignment, left_on = 'client_id', right_on = 'clientid').drop(columns='clientid')
client_data = pd.merge(client_data, internal_ref, left_on = 'pms_community_id', right_on = 'oslPropertyID')

if len(client_data) == 0:
    st.sidebar.warning('Prospect is no longer active')
    st.stop()

prospect = client_data.iloc[0]

tool_args, merged_prospect = orchestrate_merging_notes(prospect)

hellodata_property = merged_prospect['hellodata_property']
hellodata_id = merged_prospect['hellodata_id']
client_name = merged_prospect['client_full_name']

messages, average_view_full, minimum_view_full, maximum_view_full, summary_clean, availability, amenities, fees = \
    generate_summary(hellodata_property, hellodata_id, merged_prospect, concessions_history, comp_details)

summary_tab, details_tab, debug_tab = st.tabs(['AI Summary', 'Details', 'Debug'])

with summary_tab:

    st.markdown(f"""
        <div style="background-color: #f5f5f5; padding: 20px; border-radius: 6px;">
            <h2>{client_name}</h2>
            {summary_clean}
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)

with details_tab:

    with st.expander('Prospect Info'):
        st.dataframe(merged_prospect)

    with st.expander('View Available Units'):
        # selectors
        col1, col2 = st.columns([1,1])
        with col1:
            bed_count_select = st.selectbox(
                'Select Bed Count',
                options=sorted(availability['beds'].unique()),
            )
        with col2:
            agg_select = st.selectbox(
                'Select Rollup',
                options=['Individual', 'Property Average', 'Property Minimum', 'Property Maximum']
            )

        # slice out just that bed count for display
        individual_view = availability[availability['beds']==int(bed_count_select)].drop(columns='hellodata_id')
        avg_view = average_view_full[average_view_full['beds']==int(bed_count_select)]
        min_view = minimum_view_full[minimum_view_full['beds']==int(bed_count_select)]
        max_view = maximum_view_full[maximum_view_full['beds']==int(bed_count_select)]

        # show the table
        if agg_select=='Individual':
            st.dataframe(individual_view)
        elif agg_select=='Property Average':
            st.dataframe(avg_view)
        elif agg_select=='Property Maximum':
            st.dataframe(max_view)
        else:
            st.dataframe(min_view)

    with st.expander('Amenities Breakdown'):
        st.write(amenities)

    with st.expander('Fees Breakdown'):
        st.write(fees)

with debug_tab:

    with st.expander('Messages to LLM'):
        st.write(messages)