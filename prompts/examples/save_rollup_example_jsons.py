import pandas as pd
import re
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from agents.orchestrator import orchestrate_merging_notes, orchestrate_rollup_summary
from config.pull_current_date import pull_current_date

cur_date = pull_current_date()

clients = pd.read_csv(
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

group_assignment = pd.read_csv(
    "data/processed/export_group_assignment.csv",
    usecols=['clientid', 'pms_community_id'],
    dtype={'clientid': 'Int64', 'pms_community_id': 'Int64'}
)

internal_ref = pd.read_csv(
    "data/processed/hellodata_internal_ref.csv"
)

master_complist = pd.read_csv(
    "data/processed/master_complist.csv"
)

concessions_history = pd.read_csv(
    "data/raw/concessions_history.csv",
    usecols=['property_id', 'from_date', 'to_date', 'concession_text']
)

concessions_history = concessions_history[pd.to_datetime(concessions_history['to_date']) >= cur_date - pd.Timedelta(days=7)]

def pull_concessions_data(availability):
    filtered_concessions = concessions_history[concessions_history['property_id'].isin(availability['hellodata_id'])]
    filtered_concessions = pd.merge(filtered_concessions, availability[['hellodata_id', 'property']], left_on='property_id', right_on='hellodata_id').drop_duplicates()
    
    return filtered_concessions[['property', 'concession_text', 'from_date', 'to_date']]

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
    unit_history_df = unit_history_df[unit_history_df['date'] >= cur_date - pd.Timedelta(days=7)]

    return unit_history_df[['hellodata_id', 'property', 'unit_name', 'unit_group', 'sqft', 'gross_price', 'date']].drop_duplicates(subset=['unit_name'], keep='last')

def get_availability(comps, hellodata_id, prospect):
    availability = pd.DataFrame()
    for _, row in comps.iterrows():
        unit_history = pd.read_csv(f"data/raw/unit_history/{row['hellodata_id']}.csv")
        unit_history['hellodata_id'] = row['hellodata_id']
        unit_history_df = extract_unit_hist(unit_history, prospect)
        unit_history_df['internal'] = row['hellodata_id'] in set(internal_ref['hellodata_id'])
        availability = pd.concat([availability, unit_history_df], ignore_index=True)
    return availability


for funnel_id in [22215630, 18858422]:

    client_data = clients[clients['client_id'] == funnel_id]
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
        rollup['sqft']       = rollup['sqft'].round(0).astype(int)
        return rollup.sort_values(['beds','gross_price']).reset_index(drop=True)

    average_view_full = compute_rollup(availability, 'mean')
    minimum_view_full = compute_rollup(availability, 'min')
    maximum_view_full = compute_rollup(availability, 'max')

    example_input = {
        "average_view": average_view_full.to_dict(orient="records"),
        "minimum_view": minimum_view_full.to_dict(orient="records"),
        "maximum_view": maximum_view_full.to_dict(orient="records"),
        "concessions": concessions.to_dict(orient="records"),
        "prospect": merged_prospect.to_dict()
    }

    with open(f'prompts/examples/rollup_input_{funnel_id}.json', 'w') as f:
        json.dump(example_input, f, indent=2)