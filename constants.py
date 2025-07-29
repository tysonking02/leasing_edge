"""
Constants used throughout the Leasing Edge application.
"""

# Data file paths
DATA_PATHS = {
    'clients': 'data/processed/export_clients.csv',
    'group_assignment': 'data/processed/export_group_assignment.csv',
    'internal_ref': 'data/processed/hellodata_internal_ref.csv',
    'master_complist': 'data/processed/master_complist.csv',
    'concessions': 'data/raw/concessions_history.csv',
    'comp_details': 'data/processed/comp_details.csv'
}

# Client data columns
CLIENT_COLUMNS = [
    'client_id', 'client_email', 'client_full_name', 'client_status', 
    'laundry_preference', 'outdoor_space_preference', 'parking_preference', 
    'pet_preference', 'notes',
    'studio_preference', 'onebed_preference', 'twobed_preference', 
    'threebed_preference', 'fourbed_preference'
]

# Client data types
CLIENT_DTYPES = {
    'client_id': int, 
    'client_email': str, 
    'client_full_name': str, 
    'client_status': str, 
    'laundry_preference': str, 
    'outdoor_space_preference': str, 
    'parking_preference': str, 
    'pet_preference': str,
    'studio_preference': bool, 
    'onebed_preference': bool, 
    'twobed_preference': bool, 
    'threebed_preference': bool, 
    'fourbed_preference': bool, 
    'notes': str
}

# Group assignment columns and types
GROUP_ASSIGNMENT_COLUMNS = ['clientid', 'pms_community_id']
GROUP_ASSIGNMENT_DTYPES = {'clientid': 'Int64', 'pms_community_id': 'Int64'}

# Comp details columns
COMP_DETAILS_COLUMNS = [
    'asset', 'hellodata_id', 'year_built', 'cats_monthly_rent', 'cats_one_time_fee', 
    'cats_deposit', 'dogs_monthly_rent', 'dogs_one_time_fee', 'dogs_deposit',
    'admin_fee', 'amenity_fee', 'application_fee', 'storage_fee', 
    'property_quality', 'building_amenities', 'unit_amenities'
]

# Concessions columns
CONCESSIONS_COLUMNS = ['property_id', 'from_date', 'to_date', 'concession_text']

# Bedroom preferences mapping
BEDROOM_PREFERENCES = {
    0: 'studio_preference',
    1: 'onebed_preference',
    2: 'twobed_preference',
    3: 'threebed_preference',
    4: 'fourbed_preference'
}

BEDROOM_DISPLAY_NAMES = {
    0: 'Studio',
    1: '1 Bed',
    2: '2 Bed',
    3: '3 Bed',
    4: '4 Bed'
}

# Time constants
DAYS_LOOKBACK = 7

# UI Constants
SIDEBAR_WIDTH = 500
AGGREGATION_OPTIONS = ['Individual', 'Property Average', 'Property Minimum', 'Property Maximum']

# Example clients display columns
EXAMPLE_CLIENT_COLUMNS = ['client_id', 'client_full_name', 'ParentAssetName']