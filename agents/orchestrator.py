import json
import pandas as pd
import streamlit as st

from logic.llm_client import call_openai_with_functions
from prompts.system.generate_prompts import build_rollup_summary_prompt, build_note_extraction_prompt
from functions.function_specs import rollup_summary_spec, note_extraction_specs, transcript_parsing_specs
from logic.merge_data import merge_data
from logic.transcript_parser import get_transcript_data
from prompts.system.generate_prompts import build_parse_transcript_prompt


def load_query_examples(path):
    with open(path, "r") as f:
        return json.load(f)
    
def orchestrate_transcript_parsing(client_id):
    """
    Parse transcript data for a given client ID and return extracted preferences.
    
    Args:
        client_id (str): The client ID to parse transcript for
        
    Returns:
        tuple: (extracted_data_dict, dataframe_with_preferences, transcript_text)
    """
    try:
        # Get transcript data from database
        transcript, df = get_transcript_data(client_id)
        
        # If no transcript found, return empty results
        if transcript is None or df.empty:
            return {}, pd.DataFrame(), ''
        
        # Get system prompt for transcript parsing
        system_prompt = build_parse_transcript_prompt()
        
        # Construct messages for OpenAI call
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcript}
        ]
        
        response = call_openai_with_functions(
            function_specs=transcript_parsing_specs,
            messages=messages
        )
        
        extracted_preferences = {}
        try:
            tool_calls = response.choices[0].message.tool_calls
            if tool_calls and tool_calls[0].function.name == "transcript_parsing":
                extracted_preferences = json.loads(tool_calls[0].function.arguments)
        except Exception:
            pass
        
        for key, value in extracted_preferences.items():
            if value:
                # Escape dollar signs to prevent markdown formatting issues
                escaped_value = str(value).replace('$', r'\$')
                df.at[0, key] = escaped_value

        if 'transcript' in df.columns:
            df = df.drop(columns=['transcript'])
        
        return extracted_preferences, df, transcript
        
    except Exception as e:
        return {}, pd.DataFrame(), ''

def orchestrate_merging_notes(prospect):
    if prospect['notes']:
        return {}, prospect
    
    system_prompt = build_note_extraction_prompt()

    # 2. Load few-shot examples
    examples = load_query_examples(path="prompts/examples/extraction_examples.json")

    # 3. Construct messages
    messages = [{"role": "system", "content": system_prompt}]
    for ex in examples:
        messages.append({"role": "user", "content": ex["user"]})
        messages.append({
            "role": "assistant",
            "content": None,
            "function_call": {
                "name": ex["function_call"]["name"],
                "arguments": json.dumps(ex["function_call"]["arguments"])
            }
        })
    messages.append({"role": "user", "content": prospect['notes']})

    # 4. Call OpenAI with function schema
    response = call_openai_with_functions(
        function_specs=note_extraction_specs,
        messages=messages
    )

    tool_args = {}
    try:
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls and tool_calls[0].function.name == "note_extraction":
            tool_args = json.loads(tool_calls[0].function.arguments)
    except Exception:
        pass

    merged_prospect = merge_data(prospect, tool_args)
    return tool_args, merged_prospect


def orchestrate_rollup_summary(average_view, minimum_view, largest_view, concessions, amenities, fees, prospect):
    # 1. Load system prompt
    system_prompt = build_rollup_summary_prompt()

    examples = load_query_examples(path="prompts/examples/rollup_examples.json")

    messages = [{"role": "system", "content": system_prompt}]
    # for ex in examples:
    #     messages.append({
    #         "role": "user",
    #         "content": json.dumps(ex["input"], indent=2)
    #     })
    #     messages.append({
    #         "role": "assistant",
    #         "content": ex["output"]
    #     })


    messages.append({
        "role": "user",
        "content": "Please generate a summary based on the following data."
    })

    messages.append({
        "role": "assistant",
        "content": None,
        "function_call": {
            "name": "rollup_summary",
            "arguments": json.dumps({
                "average_view": average_view.to_dict(orient="records"),
                "minimum_view": minimum_view.to_dict(orient="records"),
                "largest_view": largest_view.to_dict(orient="records"),
                "concessions": concessions.to_dict(orient="records"),
                "amenities": amenities.to_dict(orient="records"),
                "fees": fees.to_dict(orient="records"),
                "prospect": prospect.to_dict()
            })
        }
    })

    # 3. Call OpenAI
    response = call_openai_with_functions(
        function_specs=rollup_summary_spec,
        messages=messages,
        tool_choice='none'
    )

    # 4. Parse and return summary
    try:
        return messages, response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"Failed to extract summary: {e}\n{response.choices[0]}")