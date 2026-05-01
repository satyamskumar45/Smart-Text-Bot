from copy import deepcopy
from datetime import date, datetime


def serialize(doc):
    if not doc:
        return doc

    data = deepcopy(doc)
    data["id"] = str(data["_id"])
    del data["_id"]
    return _normalize(data)


def _normalize(value):
    if isinstance(value, dict):
        return {key: _normalize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value
