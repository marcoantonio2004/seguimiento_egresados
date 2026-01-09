import psycopg2
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:igtByEgYBKnvijJVXtZjhXQIeixcKmlU@tramway.proxy.rlwy.net:21961/railway"
)

def get_connection():
    return psycopg2.connect(DATABASE_URL)
