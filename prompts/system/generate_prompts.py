import json
import pandas as pd
from datetime import datetime

def build_note_extraction_prompt():
    # Load template
    with open("prompts/system/note_extraction_template.txt", encoding="utf-8") as f:
        template = f.read()

    # Replace placeholders
    # prompt = (
    #     template
    #     .replace("{{today}}", datetime.today().strftime("%Y-%m-%d"))
    # )

    return template

def build_rollup_summary_prompt():
    # Load template
    with open("prompts/system/rollup_summary_template.txt", encoding="utf-8") as f:
        template = f.read()

    return template