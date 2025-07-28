import os
import openai
import yaml
from dotenv import load_dotenv
import streamlit as st 
import json

def load_settings(path="config/settings.yaml"):
    with open(path, "r") as f:
        config = yaml.safe_load(f)

    load_dotenv()
    config["openai"]["api_key"] = os.getenv("API_KEY") or st.secrets.get("API_KEY")

    return config

def auth():
    config = load_settings()

    client = openai.AzureOpenAI(
        azure_endpoint = config["openai"]["azure_endpoint"],
        api_key = config["openai"]["api_key"],
        api_version = config["openai"]["api_version"]
    )

    return client

def call_openai_with_functions(function_specs, messages, tool_choice = 'auto'):
    client = auth()
    config = load_settings()

    tools = [{"type": "function", "function": fn} for fn in function_specs]

    response = client.chat.completions.create(
        model = config["openai"]["deployment"],
        messages = messages,
        tools = tools,
        tool_choice = tool_choice
    )

    return response

