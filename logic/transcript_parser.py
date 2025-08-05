from databricks import sql as dbsql
import pandas as pd
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()

DATABRICKS_SERVER_HOSTNAME = os.getenv('DATABRICKS_SERVER_HOSTNAME') or st.secrets.get("DATABRICKS_SERVER_HOSTNAME")
DATABRICKS_HTTP_PATH = os.getenv('DATABRICKS_HTTP_PATH') or st.secrets.get("DATABRICKS_HTTP_PATH")
DATABRICKS_ACCESS_TOKEN = os.getenv('DATABRICKS_ACCESS_TOKEN') or st.secrets.get("DATABRICKS_ACCESS_TOKEN")


def get_transcript_data(client_id):
    """
    Retrieve and format transcript data from database.
    
    Args:
        client_id (str): The client ID to retrieve transcript for
    
    Returns:
        tuple: (formatted_transcript, client_df) or (None, empty_df) if no data found
    """
    # connect to databricks
    con = dbsql.connect(
        server_hostname=DATABRICKS_SERVER_HOSTNAME,
        http_path=DATABRICKS_HTTP_PATH,
        access_token=DATABRICKS_ACCESS_TOKEN
    )

    # get transcript from the table
    query = f"""
        SELECT client_id, transcript 
        FROM qaqc_graded_calls
        WHERE client_id = '{client_id}'
    """

    df = pd.read_sql(query, con)

    # close connections
    con.close()

    # if no transcript found, return None and empty dataframe
    if df.empty:
        return None, pd.DataFrame()

    # concatenate all transcripts with \n\n between them
    transcript = "\n\n".join(df["transcript"].tolist())
    
    # format speaker labels and convert newlines for HTML display
    transcript = transcript.replace("Associate", "<br><br>**Associate**")
    transcript = transcript.replace("Customer", "<br><br>**Customer**")
    transcript = transcript.replace('$', r'\$').strip()

    return transcript, df