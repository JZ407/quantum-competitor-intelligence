"""
Build conference SQLite database from JSON cache.
"""
import os, sys, json, sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conferences.db')
JSON_PATH = 'D:/Claude_code/rag_system/data/conferences_zh.json'


def main():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_str TEXT NOT NULL,
            month INTEGER NOT NULL,
            name_zh TEXT NOT NULL,
            location_zh TEXT NOT NULL,
            url TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Clear and re-import
    cursor.execute('DELETE FROM conferences')

    for c in data:
        cursor.execute(
            'INSERT INTO conferences (date_str, month, name_zh, location_zh, url) VALUES (?, ?, ?, ?, ?)',
            (c['date_str'], c['month'], c['name_zh'], c['location_zh'], c.get('url', ''))
        )

    conn.commit()
    conn.close()
    print(f'[OK] Imported {len(data)} conferences to {DB_PATH}')


if __name__ == '__main__':
    main()
