import psycopg2
from psycopg2.extras import NamedTupleCursor

import common as CONFIG


def get_db_connection():
    return psycopg2.connect(user=CONFIG.DB['user'],
                            password=CONFIG.DB['password'],
                            host=CONFIG.DB['host'],
                            port=CONFIG.DB['portnumber'],
                            database=CONFIG.DB['dbname'],
                            cursor_factory=NamedTupleCursor)
def ensure_db_connection(func):
    db_connection = None

    def inner(*args, **kwargs):
        nonlocal db_connection
        if db_connection is None or db_connection.closed:
            db_connection = get_db_connection()
        
        try:
            result = func(*args, **kwargs, db_connection=db_connection)
            db_connection.commit()
            return result
        except Exception as e:
            db_connection.close()
            raise e

    return inner