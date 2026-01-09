import psycopg2
import psycopg2.extras
import os

DATABASE_URL = os.environ.get("postgresql://postgres:igtByEgYBKnvijJVXtZjhXQIeixcKmlU@tramway.proxy.rlwy.net:21961/railway")

def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn
