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

def generate_transcript_parsing_specs():
    properties = {
        "bedrooms": {
            "type": "string",
            "description": "Bedroom preferences mentioned in the transcript"
        },
        "bathrooms": {
            "type": "string", 
            "description": "Bathroom preferences mentioned in the transcript"
        },
        "pet": {
            "type": "string",
            "description": "Pet-related requirements or mentions from the transcript"
        },
        "floor": {
            "type": "string",
            "description": "Floor preferences mentioned in the transcript"
        },
        "laundry": {
            "type": "string",
            "description": "Laundry preferences or requirements from the transcript"
        },
        "parking": {
            "type": "string",
            "description": "Parking requirements or preferences mentioned"
        },
        "amenities": {
            "type": "string",
            "description": "Desired amenities mentioned in the transcript"
        },
        "storage": {
            "type": "string",
            "description": "Storage requirements mentioned in the transcript"
        },
        "lease_term": {
            "type": "string",
            "description": "Lease term preferences mentioned in the transcript"
        },
        "move_in_date": {
            "type": "string",
            "description": "Move-in date mentioned in the transcript"
        },
        "elevator": {
            "type": "string",
            "description": "Elevator preferences mentioned in the transcript"
        },
        "additional_info": {
            "type": "string",
            "description": "Any other important information about the prospect that can be used for selling a unit."
        }
    }
    
    return [
        {
            "name": "transcript_parsing",
            "description": "Extract structured client preferences from call transcripts",
            "parameters": {
                "type": "object",
                "properties": properties
            }
        }
    ]

note_extraction_specs = generate_note_extraction_specs()
rollup_summary_spec = generate_rollup_summary_spec()
transcript_parsing_specs = generate_transcript_parsing_specs()