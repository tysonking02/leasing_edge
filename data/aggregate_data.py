import pandas as pd

export_clients = pd.read_parquet('data/raw/export_clients')

layout_types = {
    'Studio': 'studio_preference',
    '1 Bedroom': 'onebed_preference',
    '2 Bedroom': 'twobed_preference',
    '3 Bedroom': 'threebed_preference',
    '4 Bedroom': 'fourbed_preference'
}

export_clients['layout_preference'] = export_clients['layout_preference'].fillna('')

for layout, col_name in layout_types.items():
    export_clients[col_name] = export_clients['layout_preference'].str.contains(layout, na=False)

export_clients = export_clients[export_clients['client_status'].isin(['Prospect', 'Toured'])]

# filter to last 6 months of prospects
export_clients = export_clients[pd.to_datetime(export_clients['created_at']) >= pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=180)]

export_clients.to_csv('data/processed/export_clients.csv')
export_clients.head(10).to_csv('export_clients_head.csv')

export_group_assignment = pd.read_parquet('data/raw/export_group_assignment')

export_group_assignment = export_group_assignment[export_group_assignment['clientid'].isin(export_clients['client_id'])]

export_group_assignment.to_csv('data/processed/export_group_assignment.csv')
export_group_assignment.head(10).to_csv('export_group_assignment_head.csv')