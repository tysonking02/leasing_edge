import pandas as pd
import streamlit as st
import base64

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
        try:
            unit_history = pd.read_csv(f"data/raw/unit_history/{row['hellodata_id']}.csv")
            
            # Check if CSV is empty
            if unit_history.empty:
                is_internal = row['hellodata_id'] in set(internal_ref['hellodata_id'])
                if is_internal:
                    st.error(f"Internal property {row['property']} has no unit history data")
                    return pd.DataFrame()  # Return empty to stop processing
                else:
                    # Skip external comps with empty data
                    continue
            
            unit_history['hellodata_id'] = row['hellodata_id']
            unit_history_df = extract_unit_hist(unit_history, prospect)
            unit_history_df['internal'] = row['hellodata_id'] in set(internal_ref['hellodata_id'])
            availability = pd.concat([availability, unit_history_df], ignore_index=True)
            
        except (pd.errors.EmptyDataError, FileNotFoundError) as e:
            is_internal = row['hellodata_id'] in set(internal_ref['hellodata_id'])
            if is_internal:
                st.error(f"Internal property {row['property']} has missing or invalid unit history data")
                return pd.DataFrame()  # Return empty to stop processing
            else:
                # Skip external comps with missing/invalid data
                continue
                
    return availability

def pull_concessions_data(availability, concessions_history):
    filtered_concessions = concessions_history[concessions_history['property_id'].isin(availability['hellodata_id'])]
    filtered_concessions = pd.merge(filtered_concessions, availability[['hellodata_id', 'property']], left_on='property_id', right_on='hellodata_id').drop_duplicates()
    
    # Add internal flag
    filtered_concessions['internal'] = filtered_concessions['hellodata_id'].isin(set(internal_ref['hellodata_id']))
    
    return filtered_concessions[['property', 'concession_text', 'from_date', 'to_date', 'internal']]

def pull_fees_data(availability, comp_details):
    fees = comp_details[['asset', 'hellodata_id', 'cats_monthly_rent', 'cats_one_time_fee', 'cats_deposit', 'dogs_monthly_rent', 'dogs_one_time_fee', 
                         'dogs_deposit', 'admin_fee', 'amenity_fee', 'application_fee', 'storage_fee']]
    
    filtered_fees = fees[fees['hellodata_id'].isin(availability['hellodata_id'])].copy()
    
    # Round all fee columns to whole numbers
    fee_columns = ['cats_monthly_rent', 'cats_one_time_fee', 'cats_deposit', 'dogs_monthly_rent', 'dogs_one_time_fee', 
                   'dogs_deposit', 'admin_fee', 'amenity_fee', 'application_fee', 'storage_fee']
    
    for col in fee_columns:
        filtered_fees[col] = filtered_fees[col].round(0).astype('Int64')
    
    # Add internal flag
    filtered_fees['internal'] = filtered_fees['hellodata_id'].isin(set(internal_ref['hellodata_id']))

    return filtered_fees

def pull_amenities(availability, comp_details):
    amenities = comp_details[['asset', 'year_built', 'hellodata_id', 'building_amenities', 'unit_amenities']]
    filtered = amenities[amenities['hellodata_id'].isin(availability['hellodata_id'])].copy()

    def has_amenity(amenity_list, target):
        if amenity_list is None:
            return False
        if isinstance(amenity_list, str):
            return target in amenity_list
        if hasattr(amenity_list, '__iter__'):
            return target in amenity_list
        return False

    target_amenities = [
        # Essential building amenities
        'swimming_pool', 'fitness_center', 'community_dog_park', 'pets_allowed', 'parking_garage',
        'valet_trash_service', 'package_receiving', 'on_site_maintenance', 'controlled_access',
        'business_center', 'club_house_party_room', 'barbecue_grill', 'hot_tub', 'tennis_court',
        'electric_car_charging_station', 'elevator',
        
        # Key unit amenities  
        'washer_dryer_in_unit', 'air_conditioning', 'dishwasher', 'patio_or_balcony', 'walk_in_closet',
        'granite_countertops', 'quartz_countertops', 'stainless_steel_appliances', 'hardwood_floor',
        'high_ceilings', 'kitchen_island', 'fireplace', 'smart_thermostat', 'garbage_disposal'
    ]

    for amenity in target_amenities:
        filtered[amenity] = filtered.apply(
            lambda row: has_amenity(row['building_amenities'], amenity) or has_amenity(row['unit_amenities'], amenity),
            axis=1
        )

    # Add internal flag before grouping
    filtered['internal'] = filtered['hellodata_id'].isin(set(internal_ref['hellodata_id']))
    
    # Round year_built to whole number
    filtered['year_built'] = filtered['year_built'].round(0).astype('Int64')

    agg_amenities = (
        filtered.groupby(['asset', 'year_built', 'internal'])[target_amenities]
        .any()
        .reset_index()
    )

    return agg_amenities

master_complist = pd.read_csv("data/processed/master_complist.csv")
internal_ref = pd.read_csv("data/processed/hellodata_internal_ref.csv")

def style_internal_assets(df):
    """Apply styling to highlight internal asset rows with #a6cf54 background"""
    def highlight_internal(row):
        if 'internal' in row.index and row['internal']:
            return ['background-color: #a6cf54'] * len(row)
        else:
            return [''] * len(row)
    
    return df.style.apply(highlight_internal, axis=1)


def generate_summary(hellodata_property, hellodata_id, merged_prospect, concessions_history, comp_details):

    img_container = st.empty()

    with open("pug-run.gif", "rb") as file_:
        data_url = base64.b64encode(file_.read()).decode("utf-8")

    img_container.markdown(
        f'''
        <style>
        @keyframes movePug {{
            0% {{
                transform: translateX(-100px);
            }}
            100% {{
                transform: translateX(calc(100vw - 75px));
            }}
        }}
        .pug-container {{
            position: fixed;
            top: 50%;
            left: 0;
            width: 100%;
            height: 75px;
            transform: translateY(-50%);
            overflow: hidden;
            z-index: 1000;
            pointer-events: none;
        }}
        .moving-pug {{
            position: absolute;
            width: 75px;
            height: auto;
            animation: movePug 5s linear infinite;
        }}
        </style>
        <div class="pug-container">
            <img src="data:image/gif;base64,{data_url}" alt="pug gif" class="moving-pug">
        </div>
        ''',
        unsafe_allow_html=True,
    )

    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Add CSS and JavaScript to center progress bar and status text
    st.markdown(
        """
        <style>
        .centered-progress {
            position: fixed !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            background: rgba(255, 255, 255, 0.9) !important;
            padding: 20px !important;
            border-radius: 10px !important;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1) !important;
            width: 400px !important;
            text-align: center !important;
            z-index: 1001 !important;
        }
        </style>
        <script>
        setTimeout(function() {
            // Find the progress bar and text elements
            const progressBar = document.querySelector('.stProgress');
            const textElements = document.querySelectorAll('[data-testid="stText"]');
            
            if (progressBar) {
                progressBar.classList.add('centered-progress');
            }
            
            textElements.forEach(function(textEl) {
                if (textEl.textContent.includes('🔍') || textEl.textContent.includes('🏢') || 
                    textEl.textContent.includes('💰') || textEl.textContent.includes('🏊') || 
                    textEl.textContent.includes('📊') || textEl.textContent.includes('📈') || 
                    textEl.textContent.includes('🤖') || textEl.textContent.includes('✅')) {
                    textEl.classList.add('centered-progress');
                    textEl.style.top = '45%';
                }
            });
        }, 100);
        </script>
        """,
        unsafe_allow_html=True
    )

    # Step 1: Load property comparisons
    status_text.text('🔍 Loading property comparisons...')
    progress_bar.progress(10)
    comps = master_complist[master_complist['property'] == hellodata_property]
    
    # Check if property has any comps
    if len(comps) == 0:
        progress_bar.empty()
        status_text.empty()
        st.error(f"This property ({hellodata_property}) has no listed comps")
        return None, None, None, None, None, None, None, None
    
    # Step 2: Process unit availability
    status_text.text('🏢 Processing unit availability data...')
    progress_bar.progress(30)
    availability = get_availability(comps, hellodata_id, merged_prospect)
    if len(availability) == 0:
        progress_bar.empty()
        status_text.empty()
        st.error("No units available for the selected bedroom preferences")
        return None, None, None, None, None, None, None, None

    # Step 3: Gather concessions data
    status_text.text('💰 Gathering concessions and pricing data...')
    progress_bar.progress(50)
    concessions = pull_concessions_data(availability, concessions_history)
    
    # Step 4: Process amenities
    status_text.text('🏊 Processing amenities data...')
    progress_bar.progress(65)
    amenities = pull_amenities(availability, comp_details)
    
    # Step 5: Calculate fees
    status_text.text('📊 Calculating fees and charges...')
    progress_bar.progress(75)
    fees = pull_fees_data(availability, comp_details)

    # Step 6: Computing rollup views
    status_text.text('📈 Computing pricing rollups and statistics...')
    progress_bar.progress(85)
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

    # Step 7: Generating AI summary
    status_text.text('🤖 Generating AI-powered market summary...')
    progress_bar.progress(95)
    messages, summary = orchestrate_rollup_summary(average_view_full, minimum_view_full, maximum_view_full, concessions, amenities, fees, merged_prospect)

    # Step 8: Finalizing
    status_text.text('✅ Summary complete!')
    progress_bar.progress(100)
    summary_clean = summary.replace('$', r'\$')
    
    # Clean up progress indicators
    import time
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()

    img_container.empty()

    return messages, average_view_full, minimum_view_full, maximum_view_full, summary_clean, availability, amenities, fees, concessions