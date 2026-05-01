import os
from threading import Lock

from pymongo import ASCENDING, MongoClient
from pymongo.errors import PyMongoError


DB_NAME = "smarttextbot"

_client = None
_db = None
_db_error = None
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


def init_db():
    global _client, _db, _db_error, _indexes_ready

    if _db is not None:
        return _db

    with _lock:
        if _db is not None:
            return _db

        try:
            _client = _build_client()

            # Verify connection
            _client.admin.command("ping")

            _db = _client[DB_NAME]

            # Ensure indexes only once
            if not _indexes_ready:
                _ensure_indexes(_db)
                _indexes_ready = True

            _db_error = None
            print("MongoDB connected successfully")

        except (PyMongoError, RuntimeError) as exc:
            _db_error = f"MongoDB connection failed: {str(exc)}"
            _client = None
            _db = None
            _indexes_ready = False
            return None

        return _db


def get_db():
    db = _db or init_db()
    if db is None:
        raise RuntimeError(_db_error or "MongoDB connection is unavailable.")
    return db


def _ensure_indexes(db):
    try:
        db.users.create_index([("email", ASCENDING)], unique=True)
        db.refresh_tokens.create_index([("token", ASCENDING)], unique=True)
        db.history.create_index([("user_id", ASCENDING)])
        db.guest_sessions.create_index([("session_id", ASCENDING)], unique=True)
        db.progress.create_index(
            [("user_id", ASCENDING), ("module", ASCENDING)],
            unique=True,
        )
    except PyMongoError as exc:
        print(f"[INDEX WARNING] Failed to create indexes: {exc}")