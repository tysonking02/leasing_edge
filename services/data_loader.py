"""
Data loading service for the Leasing Edge application.
Handles all CSV file loading with caching.
"""

import pandas as pd
import streamlit as st
from config.pull_current_date import pull_current_date
from constants import (
    DATA_PATHS, CLIENT_COLUMNS, CLIENT_DTYPES, 
    GROUP_ASSIGNMENT_COLUMNS, GROUP_ASSIGNMENT_DTYPES,
    COMP_DETAILS_COLUMNS, CONCESSIONS_COLUMNS, DAYS_LOOKBACK
)


@st.cache_data
def load_clients():
    """Load client data with proper column selection and types."""
    return pd.read_csv(
        DATA_PATHS['clients'], 
        usecols=CLIENT_COLUMNS,
        dtype=CLIENT_DTYPES
    )


@st.cache_data
def load_group_assignment():
    """Load group assignment data."""
    return pd.read_csv(
        DATA_PATHS['group_assignment'],
        usecols=GROUP_ASSIGNMENT_COLUMNS,
        dtype=GROUP_ASSIGNMENT_DTYPES
    )


@st.cache_data
def load_internal_ref():
    """Load internal reference data."""
    return pd.read_csv(DATA_PATHS['internal_ref'])


@st.cache_data
def load_master_complist():
    """Load master comp list data."""
    return pd.read_csv(DATA_PATHS['master_complist'])


@st.cache_data
def load_concessions():
    """Load recent concessions data (last 7 days)."""
    cur_date = pull_current_date()
    all_concessions = pd.read_csv(
        DATA_PATHS['concessions'],
        usecols=CONCESSIONS_COLUMNS
    )
    
    # Filter to recent concessions
    return all_concessions[
        pd.to_datetime(all_concessions['to_date']) >= 
        cur_date - pd.Timedelta(days=DAYS_LOOKBACK)
    ]


@st.cache_data
def load_comp_details():
    """Load competition details data."""
    return pd.read_csv(
        DATA_PATHS['comp_details'],
        usecols=COMP_DETAILS_COLUMNS
    )


def load_all_data():
    """Load all required datasets."""
    return {
        'clients': load_clients(),
        'group_assignment': load_group_assignment(),
        'internal_ref': load_internal_ref(),
        'master_complist': load_master_complist(),
        'concessions_history': load_concessions(),
        'comp_details': load_comp_details()
    }