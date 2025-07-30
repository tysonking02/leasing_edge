"""
Client service for handling client-related business logic.
"""

import pandas as pd
from constants import BEDROOM_PREFERENCES, EXAMPLE_CLIENT_COLUMNS


def get_client_data(clients, funnel_id):
    """Get client data by funnel ID."""
    return clients[clients['client_id'] == funnel_id]


def merge_client_with_assignments(client_data, group_assignment, internal_ref):
    """Merge client data with group assignments and internal references."""
    # Merge with group assignment
    client_data = pd.merge(
        client_data, 
        group_assignment, 
        left_on='client_id', 
        right_on='clientid'
    ).drop(columns='clientid')
    
    # Merge with internal reference
    client_data = pd.merge(
        client_data, 
        internal_ref, 
        left_on='pms_community_id', 
        right_on='oslPropertyID'
    )
    
    return client_data


def has_bedroom_preferences(prospect):
    """Check if prospect has any bedroom preferences set."""
    bedroom_prefs = list(BEDROOM_PREFERENCES.values())
    return any(prospect.get(pref) for pref in bedroom_prefs)


def get_selected_bedroom_preferences(prospect):
    """Get list of bedroom counts that prospect prefers."""
    selected_beds = []
    for bed_count, pref_field in BEDROOM_PREFERENCES.items():
        if prospect.get(pref_field):
            selected_beds.append(bed_count)
    return selected_beds


def set_bedroom_preferences(prospect, bed_preferences):
    """Set bedroom preferences on prospect object."""
    prospect = prospect.copy()
    for beds in bed_preferences:
        if beds in BEDROOM_PREFERENCES:
            prospect[BEDROOM_PREFERENCES[beds]] = True
    return prospect


def search_clients(clients, query, limit=10):
    """Search clients by ID or name with partial matching."""
    if not query or len(query.strip()) == 0:
        return []
    
    query = query.strip().lower()
    
    # Search by client ID (exact match first, then partial)
    exact_id_matches = clients[clients['client_id'].astype(str).str.lower() == query]
    partial_id_matches = clients[
        clients['client_id'].astype(str).str.lower().str.contains(query, na=False) & 
        (clients['client_id'].astype(str).str.lower() != query)
    ]
    
    # Search by client name (partial match)
    name_matches = clients[
        clients['client_full_name'].str.lower().str.contains(query, na=False) &
        ~clients['client_id'].astype(str).str.lower().str.contains(query, na=False)
    ]
    
    # Combine results with prioritization
    results = pd.concat([exact_id_matches, partial_id_matches, name_matches], ignore_index=True)
    
    # Remove duplicates and limit results
    results = results.drop_duplicates(subset=['client_id']).head(limit)
    
    # Format for display
    search_results = []
    for _, row in results.iterrows():
        search_results.append({
            'id': row['client_id'],
            'name': row['client_full_name'],
            'display': f"{row['client_id']} - {row['client_full_name']}"
        })
    
    return search_results


def prepare_example_clients(clients, group_assignment, internal_ref):
    """Prepare example clients data for sidebar display."""
    example_clients = pd.merge(
        clients, 
        group_assignment, 
        left_on='client_id', 
        right_on='clientid'
    )
    example_clients = pd.merge(
        example_clients, 
        internal_ref, 
        left_on='pms_community_id', 
        right_on='oslPropertyID'
    )
    
    result = example_clients[EXAMPLE_CLIENT_COLUMNS].sort_values(
        'client_id', 
        ascending=False
    ).reset_index(drop=True)
    
    # Rename columns for display
    result = result.rename(columns={
        'client_id': 'Client ID',
        'client_full_name': 'Client Name', 
        'ParentAssetName': 'Asset'
    })
    
    return result