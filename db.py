import psycopg2
import psycopg2.extras
import os

DATABASE_URL = os.environ.get("DATABASE_PUBLIC_URL")

def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn
