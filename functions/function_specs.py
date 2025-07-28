def generate_note_extraction_specs():
    properties = {
        "client_full_name": {
            "type": "string",
            "description": "The prospect's full name"
        },
        "client_price_ceiling": {
            "type": "integer",
            "description": "Max price that the prospect is willing to pay"
        },
        "client_sqft_min": {
            "type": "integer",
            "description": "Minimum square footage that the prospect wants"
        },        
        "studio_preference": {
            "type": "boolean",
            "description": "The prospect is interested in a studio (0 bed)"
        },
        "onebed_preference": {
            "type": "boolean",
            "description": "The prospect is interested in a 1 bedroom apartment"
        },
        "twobed_preference": {
            "type": "boolean",
            "description": "The prospect is interested in a 2 bedroom apartment"
        },
        "threebed_preference": {
            "type": "boolean",
            "description": "The prospect is interested in a 3 bedroom apartment"
        },
        "fourbed_preference": {
            "type": "boolean",
            "description": "The prospect is interested in a 4 bedroom apartment"
        }
    }
        
    return [
        {
            "name": "note_extraction",
            "description": "Extract structured detail from manually inputted notes",
            "parameters": {
                "type": "object",
                "properties": properties
            }
        }
    ]

def generate_rollup_summary_spec():
    return [
        {
            "name": "rollup_summary",
            "description": "Generate a free-form summary of a prospect's preferences and how the available options compare",
            "parameters": {
                "type": "object",
                "properties": {
                    "average_view": {
                        "type": "array",
                        "description": "A list of average rollups by property",
                        "items": {"type": "object"}
                    },
                    "minimum_view": {
                        "type": "array",
                        "description": "A list of minimum rollups by property",
                        "items": {"type": "object"}
                    },
                    "largest_view": {
                        "type": "array",
                        "description": "A list of the largest units for that bed count",
                        "items": {"type": "object"}
                    },
                    "concessions": {
                        "type": "array",
                        "description": "A list of concessions for the property and its comps",
                        "items": {"type": "object"}
                    },
                    "amenities": {
                        "type": "array",
                        "description": "A list of the building and unit amenities for that property",
                        "items": {"type": "object"}
                    },
                    "fees": {
                        "type": "array",
                        "description": "A list of the fees for that property",
                        "items": {"type": "object"}
                    },
                    "prospect": {
                        "type": "object",
                        "description": "Merged client data including preferences"
                    }
                },
                "required": ["average_view", "minimum_view", "largest_view", "concessions", "amenities", "fees", "prospect"]
            }
        }
    ]

note_extraction_specs = generate_note_extraction_specs()
rollup_summary_spec = generate_rollup_summary_spec()