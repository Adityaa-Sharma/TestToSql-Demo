import psycopg2
from psycopg2 import sql
import contextlib
from contextlib import contextmanager
import uuid
import asyncio
from typing import Union, Any
import json

# Database connection parameters
db_params = {
                     
}


@contextlib.contextmanager
def get_db_connection():
    conn = psycopg2.connect(**db_params)
    try:
        yield conn
    finally:
        conn.close()

@contextlib.contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as connection:
        cursor = connection.cursor()
        try:
            yield cursor
            if commit:
                connection.commit()
        finally:
            cursor.close()



