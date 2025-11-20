LLM_RESPONSE_SCHEMA = {
    "name": "classification_result",
    "schema": {
        "type": "object",
        "additionalProperties": {
            "type": "array",
            "items": {"type": "string"}
        },
        "description": "Grouped classification result where keys are the classes."
    },
    "strict": True
}