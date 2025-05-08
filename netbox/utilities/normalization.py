def normalize_empty_strings(data) -> dict:
    """
    Replace empty strings with None, but only for specific fields that safely accept null.
    This avoids touching fields like 'label' that are NOT NULL in the database.
    """
    if not isinstance(data, dict):
        return data  # Safe fallback — do nothing

    # List of fields that are known to accept None (safely nullable)
    nullable_fields = {
        "wwn",
        "mode",
        "_name",
        "rf_role",
        "rf_channel",
        "duplex",
        "poe_mode",
        "poe_type",
        "cable_end",
    }

    return {
        key: (None if key in nullable_fields and isinstance(value, str) and not value.strip() else value)
        for key, value in data.items()
    }
