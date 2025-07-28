import pandas as pd

def merge_data(prospect, args):
    prospect = prospect.copy()

    if args.get('client_full_name') and pd.isna(prospect['client_full_name']):
        prospect['client_full_name'] = args['client_full_name']

    if 'client_price_ceiling' in args and pd.isna(prospect['client_price_ceiling']):
        prospect['client_price_ceiling'] = args['client_price_ceiling']

    for field in ['studio_preference', 'onebed_preference', 'twobed_preference', 'threebed_preference', 'fourbed_preference']:
        if field in args:
            prospect[field] = args[field]

    return prospect