import os
from threading import Lock

from pymongo import ASCENDING, MongoClient
from pymongo.errors import PyMongoError


DEFAULT_DB_NAME = "smarttextbot"

_client = None
_db = None
_indexes_ready = False
_lock = Lock()


def _build_client():
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise RuntimeError("MONGO_URI environment variable is required.")

    return MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
        retryWrites=True,
    )


def _get_database_name():
    return os.getenv("MONGO_DB_NAME", DEFAULT_DB_NAME).strip() or DEFAULT_DB_NAME

def init_db():
    global _client, _db, _indexes_ready

    # If DB already initialized, return it
    if _db is not None:
        return _db

    with _lock:
        # Double-check inside lock
        if _db is not None:
            return _db

        try:
            client = _build_client()

            # Test connection
            client.admin.command("ping")

            # Get database
            database = client[_get_database_name()]

            # Ensure indexes
            _ensure_indexes(database)

            # 🔥 CRITICAL FIX: assign globals
            _client = client
            _db = database
            _indexes_ready = True

            return _db

        except (PyMongoError, RuntimeError) as exc:
            # Reset state on failure
            _client = None
            _db = None
            _indexes_ready = False

            raise RuntimeError(f"MongoDB connection failed: {exc}") from exc

        _client = client
        _db = database
        _indexes_ready = True
        return _db


def get_db():
    global _db
    if _db is None:
        return init_db()
    return _db


def _ensure_indexes(db): 
    if _indexes_ready:
        return

    db.users.create_index([("email", ASCENDING)], unique=True, background=True)
    db.refresh_tokens.create_index([("token", ASCENDING)], unique=True, background=True)
    db.refresh_tokens.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0, background=True)
    db.refresh_tokens.create_index([("user_id", ASCENDING)], background=True)
    db.guest_sessions.create_index([("session_id", ASCENDING)], unique=True, background=True)
    db.history.create_index([("user_id", ASCENDING), ("created_at", ASCENDING)], background=True)
    db.history.create_index([("guest_session_id", ASCENDING), ("created_at", ASCENDING)], background=True)
    db.progress.create_index(
        [("user_id", ASCENDING), ("module", ASCENDING)],
        unique=True,
        background=True,
    )
    db.learning_progress.create_index([("user_id", ASCENDING)], unique=True, background=True)
    db.streak_tracking.create_index([("user_id", ASCENDING)], unique=True, background=True)
