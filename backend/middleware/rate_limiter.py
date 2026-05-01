from flask import request
from datetime import datetime, timedelta
from config.settings import Settings
from utils.response import error

_rate_store = {}


def enforce_rate_limit():
    if not Settings.RATE_LIMIT_ENABLED:
        return None

    identifier = request.remote_addr or 'unknown'
    route = request.endpoint or request.path
    now = datetime.utcnow()
    entry = _rate_store.get(identifier)

    if not entry or now - entry['window_start'] >= timedelta(minutes=1):
        _rate_store[identifier] = {
            'window_start': now,
            'count': 1,
        }
        return None

    entry['count'] += 1
    if entry['count'] > Settings.RATE_LIMIT_PER_MINUTE:
        return error('Too many requests, please try again later.', 429)

    return None
