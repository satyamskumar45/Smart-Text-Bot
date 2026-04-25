import mysql.connector
from mysql.connector import pooling, Error as MySQLError
from config.settings import Settings

_db_pool = None


def get_db():
    global _db_pool
    if _db_pool is None:
        print(f"[DB CONNECT] creating connection pool with host={Settings.DB_HOST}, user={Settings.DB_USER}, database={Settings.DB_NAME}")
        try:
            _db_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name=Settings.DB_POOL_NAME,
                pool_size=Settings.DB_POOL_SIZE,
                host=Settings.DB_HOST,
                user=Settings.DB_USER,
                password=Settings.DB_PASSWORD,
                database=Settings.DB_NAME,
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
        return _db_pool.get_connection()
    except MySQLError as exc:
        print(f"[DB CONNECTION ERROR] failed to get connection from pool: {exc}")
        raise RuntimeError("Database connection failed") from exc
