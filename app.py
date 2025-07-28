import pandas as pd
import streamlit as st
import re

from agents.orchestrator import orchestrate_merging_notes, orchestrate_rollup_summary

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
def get_availability(comps, hellodata_id, prospect):
    availability = pd.DataFrame()
    for _, row in comps.iterrows():
        unit_history = pd.read_csv(f"data/raw/unit_history/{row['hellodata_id']}.csv")
        unit_history['hellodata_id'] = row['hellodata_id']
        unit_history_df = extract_unit_hist(unit_history, prospect)
        unit_history_df['internal'] = row['hellodata_id'] in set(internal_ref['hellodata_id'])
        availability = pd.concat([availability, unit_history_df], ignore_index=True)
    return availability

def extract_unit_hist(unit_history, prospect):
    unit_history_df = unit_history.copy()

    # Extract bed and bath counts from 'unit_group' like '1x1'
    unit_history_df[['bed_count', 'bath_count']] = unit_history_df['unit_group'].str.extract(r'(\d+)x(\d+)').astype(int)

    # Filter using the bed preference booleans in the prospect
    preferred_beds = []
    if prospect.get('studio_preference'): preferred_beds.append(0)
    if prospect.get('onebed_preference'): preferred_beds.append(1)
    if prospect.get('twobed_preference'): preferred_beds.append(2)
    if prospect.get('threebed_preference'): preferred_beds.append(3)
    if prospect.get('fourbed_preference'): preferred_beds.append(4)

    unit_history_df = unit_history_df[unit_history_df['bed_count'].isin(preferred_beds)]

    # Parse and filter by date (past 7 days)
    unit_history_df['date'] = pd.to_datetime(unit_history_df['date'])
    unit_history_df = unit_history_df[unit_history_df['date'] >= pd.Timestamp.now() - pd.Timedelta(days=7)]

    return unit_history_df[['hellodata_id', 'property', 'unit_name', 'unit_group', 'sqft', 'gross_price', 'date']].drop_duplicates(subset=['unit_name'], keep='last')

def pull_concessions_data(availability):
    filtered_concessions = concessions_history[concessions_history['property_id'].isin(availability['hellodata_id'])]
    filtered_concessions = pd.merge(filtered_concessions, availability[['hellodata_id', 'property']], left_on='property_id', right_on='hellodata_id').drop_duplicates()
    
    return filtered_concessions[['property', 'concession_text', 'from_date', 'to_date']]

clients = load_clients()
group_assignment = load_group_assignment()
internal_ref = load_internal_ref()
master_complist = load_master_complist()
concessions_history = load_concessions()

st.sidebar.header('Leasing Edge Tool')

# with st.sidebar.expander('Find GC IDs'):
#     property_select = st.selectbox('Select Property', options=sorted(internal_ref['hellodata_property'].unique()))

with st.sidebar.expander('Example GC IDs'):
    example_ids = [22215630, 18858422]
    
    for cid in example_ids:
        st.markdown(f"- `{cid}`")

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

prospect = client_data.iloc[0]

tool_args, merged_prospect = orchestrate_merging_notes(prospect)

hellodata_property = merged_prospect['hellodata_property']
hellodata_id = merged_prospect['hellodata_id']
client_name = merged_prospect['client_full_name']

comps = master_complist[master_complist['property'] == hellodata_property]
availability = get_availability(comps, hellodata_id, merged_prospect)
concessions = pull_concessions_data(availability)

availability['beds'] = availability['unit_group'].str.split('x').str[0].astype(int)

def compute_rollup(df, agg_func):
    rollup = (
        df.groupby(['beds', 'internal', 'property'])
        .agg(
            gross_price=('gross_price', agg_func),
            sqft=('sqft', agg_func),
            available_units=('unit_name', 'count')
        )
        .reset_index()
    )
    rollup['gross_price'] = rollup['gross_price'].round(0).astype(int).apply(lambda x: f"${x:,}")
    rollup['sqft'] = rollup['sqft'].round(0).astype(int)
    return rollup.sort_values(['beds','gross_price']).reset_index(drop=True)

average_view_full = compute_rollup(availability, 'mean')
minimum_view_full = compute_rollup(availability, 'min')
maximum_view_full = compute_rollup(availability, 'max')

with st.spinner('Summarizing comp data...'):
    summary = orchestrate_rollup_summary(average_view_full, minimum_view_full, maximum_view_full, concessions, merged_prospect)

summary_clean = summary.replace('$', r'\$')

st.markdown(f"""
    <div style="background-color: #f5f5f5; padding: 20px; border-radius: 6px;">
        <h2>{client_name}</h2>
        {summary_clean}
        <br>
    </div>
""", unsafe_allow_html=True)

with st.expander('Prospect Info'):
    st.dataframe(merged_prospect)

# 3) Now open the expander for the detail views
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