"""
Validation service for input validation and error handling.
"""

import pandas as pd
import streamlit as st


def validate_funnel_id(funnel_id_input):
    """
    Validate and convert funnel ID input.
    
    Returns:
        tuple: (is_valid, funnel_id, error_message)
    """
    if not funnel_id_input or funnel_id_input == '':
        return False, None, "Please enter a GC ID"
    
    try:
        funnel_id = int(funnel_id_input)
        return True, funnel_id, None
    except ValueError:
        return False, None, "GC ID must be a valid number"


def validate_client_exists(client_data):
    """
    Validate that client exists in the system.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(client_data) == 0:
        return False, "Invalid GC ID - client not found"
    return True, None


def validate_client_active(merged_client_data):
    """
    Validate that client is still active.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(merged_client_data) == 0:
        return False, "Prospect is no longer active"
    return True, None


def handle_validation_error(error_message):
    """Display validation error and stop execution."""
    st.sidebar.warning(error_message)
    st.stop()


def safe_get_prospect_data(merged_client_data):
    """
    Safely extract prospect data from merged client data.
    
    Returns:
        pd.Series: First row of client data
    """
    if len(merged_client_data) == 0:
        return None
    return merged_client_data.iloc[0]