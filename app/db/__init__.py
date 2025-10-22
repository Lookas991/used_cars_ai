import os
import psycopg2

DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/carsdb")

def get_db():
    conn = psycopg2.connect(DB_URL)
    return conn
