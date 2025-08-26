# app/database.py
import sqlite3
import json 

DATABASE_NAME = "leads.db"

def get_db_connection():
    """Creates and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    return conn

def create_leads_table():
    """Creates the 'leads' table in the database if it doesn't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_url TEXT NOT NULL UNIQUE,
            first_name TEXT,
            last_name TEXT,
            title TEXT,
            company TEXT,
            enriched_data TEXT,
            personalized_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("'leads' table created or already exists.")

# This will run when the application starts
if __name__ == '__main__':
    create_leads_table()

def check_if_lead_exists(profile_url: str) -> bool:
    """Checks if a lead with the given profile_url already exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM leads WHERE profile_url = ?", (profile_url,))
    lead = cursor.fetchone()
    conn.close()
    return lead is not None

def add_lead(lead_data: dict):
    """Adds a new, enriched lead to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leads (
            profile_url, first_name, last_name, title, company, 
            enriched_data, personalized_message
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        lead_data.get('profile_url'),
        lead_data.get('first_name'),
        lead_data.get('last_name'),
        lead_data.get('title'),
        lead_data.get('company'),
        json.dumps(lead_data.get('enriched_data')), # Convert dict to JSON string
        lead_data.get('personalized_message')
    ))
    conn.commit()
    conn.close()