import pandas as pd
import streamlit as st

from agents.orchestrator import orchestrate_rollup_summary
from config.pull_current_date import pull_current_date

cur_date = pull_current_date()

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

def pull_concessions_data(availability, concessions_history):
    filtered_concessions = concessions_history[concessions_history['property_id'].isin(availability['hellodata_id'])]
    filtered_concessions = pd.merge(filtered_concessions, availability[['hellodata_id', 'property']], left_on='property_id', right_on='hellodata_id').drop_duplicates()
    
    return filtered_concessions[['property', 'concession_text', 'from_date', 'to_date']]

def pull_fees_data(availability, comp_details):
    fees = comp_details[['asset', 'hellodata_id', 'cats_monthly_rent', 'cats_one_time_fee', 'cats_deposit', 'dogs_monthly_rent', 'dogs_one_time_fee', 
                         'dogs_deposit', 'admin_fee', 'amenity_fee', 'application_fee', 'storage_fee']]
    
    filtered_fees = fees[fees['hellodata_id'].isin(availability['hellodata_id'])].copy()

    return filtered_fees

def pull_amenities(availability, comp_details):
    amenities = comp_details[['asset', 'hellodata_id', 'building_amenities', 'unit_amenities']]
    filtered = amenities[amenities['hellodata_id'].isin(availability['hellodata_id'])].copy()

    def has_amenity(amenity_list, target):
        if amenity_list is None:
            return False
        if isinstance(amenity_list, str):
            return target in amenity_list
        if hasattr(amenity_list, '__iter__'):
            return target in amenity_list
        return False

    target_amenities = ['community_dog_park', 'swimming_pool', 'valet_trash_service', 'pets_allowed', 'spa', 'fitness_center',
                        'granite_countertops', 'quartz_countertops', 'marble_countertops']

    for amenity in target_amenities:
        filtered[amenity] = filtered.apply(
            lambda row: has_amenity(row['building_amenities'], amenity) or has_amenity(row['unit_amenities'], amenity),
            axis=1
        )

    agg_amenities = (
        filtered.groupby('asset')[target_amenities]
        .any()
        .reset_index()
    )

    return agg_amenities

master_complist = pd.read_csv("data/processed/master_complist.csv")
internal_ref = pd.read_csv("data/processed/hellodata_internal_ref.csv")

def generate_summary(hellodata_property, hellodata_id, merged_prospect, concessions_history, comp_details):
    comps = master_complist[master_complist['property'] == hellodata_property]
    availability = get_availability(comps, hellodata_id, merged_prospect)
    if len(availability) == 0:
        print('')
        return None, None, None, None, None, None, None, None

    concessions = pull_concessions_data(availability, concessions_history)
    amenities = pull_amenities(availability, comp_details)
    fees = pull_fees_data(availability, comp_details)

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

    messages, summary = orchestrate_rollup_summary(average_view_full, minimum_view_full, maximum_view_full, concessions, amenities, fees, merged_prospect)

    summary_clean = summary.replace('$', r'\$')

    return messages, average_view_full, minimum_view_full, maximum_view_full, summary_clean, availability, amenities, fees