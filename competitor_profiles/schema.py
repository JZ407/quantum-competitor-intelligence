"""Database schema and CRUD for competitor profiles."""
import sqlite3, json, os, sys
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profiles.db')


def init_profile_db() -> sqlite3.Connection:
    """Create profile tables if not exist. Returns connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Main profile table
    c.execute('''CREATE TABLE IF NOT EXISTS competitor_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        name_cn TEXT,
        founded_year INTEGER,
        hq TEXT,
        website TEXT,
        employee_count INTEGER,
        qubit_modality TEXT,
        tech_stage TEXT,
        business_model TEXT,
        ceo TEXT,
        founders JSON,
        key_people JSON,
        total_funding_usd REAL,
        funding_history JSON,
        valuation_usd REAL,
        products JSON,
        partnerships JSON,
        tech_milestones JSON,
        swot JSON,
        competitive_positioning TEXT,
        latest_summary TEXT,
        profile_status TEXT DEFAULT 'draft',
        last_researched TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Sources table — tracks where each data point came from
    c.execute('''CREATE TABLE IF NOT EXISTS profile_sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_id INTEGER REFERENCES competitor_profiles(id),
        field_name TEXT,
        source_url TEXT,
        source_title TEXT,
        extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Research log — tracks research sessions
    c.execute('''CREATE TABLE IF NOT EXISTS profile_research_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_id INTEGER REFERENCES competitor_profiles(id),
        session_type TEXT,
        queries_used TEXT,
        new_findings INTEGER DEFAULT 0,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    return conn


def get_profile(conn, company_name: str) -> dict:
    """Get a profile by company name (fuzzy). Returns dict or None."""
    c = conn.cursor()
    c.execute('SELECT * FROM competitor_profiles WHERE company_name LIKE ? OR name_cn LIKE ?',
              (f'%{company_name}%', f'%{company_name}%'))
    row = c.fetchone()
    if not row:
        return None
    d = dict(row)
    # Deserialize JSON fields
    for field in ['founders', 'key_people', 'funding_history', 'products',
                   'partnerships', 'tech_milestones', 'swot']:
        if d.get(field) and isinstance(d[field], str):
            try:
                d[field] = json.loads(d[field])
            except json.JSONDecodeError:
                pass
    return d


def upsert_profile(conn, data: dict) -> int:
    """Insert or update a profile. Returns profile id."""
    c = conn.cursor()
    # Check existing
    c.execute('SELECT id FROM competitor_profiles WHERE company_name = ?',
              (data.get('company_name', ''),))
    existing = c.fetchone()

    # Serialize JSON fields
    json_fields = ['founders', 'key_people', 'funding_history', 'products',
                   'partnerships', 'tech_milestones', 'swot']
    values = dict(data)
    for f in json_fields:
        if f in values and isinstance(values[f], (list, dict)):
            values[f] = json.dumps(values[f], ensure_ascii=False)
    values['updated_at'] = datetime.now().isoformat()

    if existing:
        pid = existing['id']
        sets = ', '.join(f'{k}=?' for k in values if k != 'id')
        params = [values[k] for k in values if k != 'id'] + [pid]
        c.execute(f'UPDATE competitor_profiles SET {sets} WHERE id=?', params)
    else:
        cols = ', '.join(values.keys())
        placeholders = ', '.join('?' * len(values))
        params = list(values.values())
        c.execute(f'INSERT INTO competitor_profiles ({cols}) VALUES ({placeholders})', params)
        pid = c.lastrowid

    conn.commit()
    return pid


def add_source(conn, profile_id: int, field_name: str, source_url: str, source_title: str = ''):
    c = conn.cursor()
    c.execute('''INSERT INTO profile_sources (profile_id, field_name, source_url, source_title)
                 VALUES (?, ?, ?, ?)''', (profile_id, field_name, source_url, source_title))
    conn.commit()


def list_profiles(conn) -> list:
    """List all profiles with summary stats."""
    c = conn.cursor()
    c.execute('''SELECT id, company_name, name_cn, qubit_modality, total_funding_usd,
                 profile_status, last_researched, updated_at
                 FROM competitor_profiles ORDER BY COALESCE(total_funding_usd, 0) DESC''')
    return [dict(r) for r in c.fetchall()]


def get_profile_sources(conn, profile_id: int) -> list:
    """Get all sources for a profile."""
    c = conn.cursor()
    c.execute('SELECT * FROM profile_sources WHERE profile_id = ? ORDER BY extracted_at DESC',
              (profile_id,))
    return [dict(r) for r in c.fetchall()]
