import os
<<<<<<< HEAD
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
            client = _build_client()
            client.admin.command("ping")
            db = client[DB_NAME]
            if not _indexes_ready:
                _ensure_indexes(db)
                _indexes_ready = True
        except (PyMongoError, RuntimeError) as exc:
            _db_error = f"MongoDB connection failed: {exc}"
            _indexes_ready = False
            return None

        _client = client
        _db = db
        _db_error = None
        print("MongoDB connected successfully")
        return _db


def get_db():
    db = _db or init_db()
    if db is None:
        raise RuntimeError(_db_error or "MongoDB connection is unavailable.")
    return db


def _ensure_indexes(db):
    db.users.create_index([("email", ASCENDING)], unique=True, sparse=True)
    db.refresh_tokens.create_index([("token", ASCENDING)], unique=True)
    db.history.create_index([("user_id", ASCENDING)])
    db.history.create_index([("user_id", ASCENDING), ("created_at", ASCENDING)])
    db.guest_sessions.create_index([("session_id", ASCENDING)], unique=True)
    db.progress.create_index([("user_id", ASCENDING), ("module", ASCENDING)], unique=True)
=======
import mysql.connector
from mysql.connector import pooling, Error as MySQLError
from config.settings import Settings

_db_pool = None


def get_db():
    global _db_pool

    if _db_pool is None:
        print(
            f"[DB CONNECT] creating connection pool with "
            f"host={Settings.DB_HOST}, "
            f"port={os.getenv('DB_PORT', '3306')}, "
            f"user={Settings.DB_USER}, "
            f"database={Settings.DB_NAME}"
        )

        try:
            _db_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name=Settings.DB_POOL_NAME,
                pool_size=Settings.DB_POOL_SIZE,
                host=Settings.DB_HOST,
                port=int(os.getenv("DB_PORT", "3306")),
                user=Settings.DB_USER,
                password=Settings.DB_PASSWORD,
                database=Settings.DB_NAME,
                connection_timeout=Settings.DB_CONNECT_TIMEOUT,
                charset="utf8mb4",
                use_unicode=True,
                autocommit=False,
            )

        except MySQLError as exc:
            msg = "Database connection failed"

            if exc.errno == 1045:
                msg = "Database connection failed: invalid MySQL credentials"

            elif exc.errno == 1049:
                msg = "Database connection failed: unknown database"

            elif exc.errno == 2003:
                msg = "Database connection failed: unable to reach MySQL server"

            print(f"[DB CONNECT ERROR] {msg} ({exc.errno}): {exc.msg}")
            raise RuntimeError(msg) from exc

    try:
        connection = _db_pool.get_connection()
        if not connection.is_connected():
            connection.reconnect(attempts=1, delay=0)
        return connection

    except MySQLError as exc:
        print(f"[DB CONNECTION ERROR] failed to get connection from pool: {exc}")
        raise RuntimeError("Database connection failed") from exc
>>>>>>> 7a39e76952f1835cf7031449b83138e654424a73
