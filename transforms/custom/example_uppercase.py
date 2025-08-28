def transform(payload: dict) -> dict:
    if isinstance(payload, dict) and "method" in payload and isinstance(payload["method"], str):
        payload = dict(payload)
        payload["method"] = payload["method"].upper()
    return payload
