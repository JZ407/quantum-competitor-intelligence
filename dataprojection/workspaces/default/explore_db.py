import sqlite3
import json

conn = sqlite3.connect(r'D:\Claude_code\dataprojection\data\dataprojection.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables:', [t[0] for t in tables])

for t in tables:
    tn = t[0]
    print(f'\n=== Table: {tn} ===')
    cursor.execute(f'PRAGMA table_info("{tn}")')
    for c in cursor.fetchall():
        print(f'  {c[1]} ({c[2]})')
    cursor.execute(f'SELECT COUNT(*) FROM "{tn}"')
    print(f'  Row count: {cursor.fetchone()[0]}')

# Sample data
for t in tables:
    tn = t[0]
    print(f'\n=== Sample from {tn} (first 5 rows) ===')
    cursor.execute(f'SELECT * FROM "{tn}" LIMIT 5')
    cols = [d[0] for d in cursor.description]
    print(f'  Columns: {cols}')
    for row in cursor.fetchall():
        # Truncate long values for display
        display_row = []
        for val in row:
            if isinstance(val, str) and len(val) > 200:
                display_row.append(val[:200] + '...')
            else:
                display_row.append(val)
        print(f'  {display_row}')

# Check for investment/financing related data
for t in tables:
    tn = t[0]
    cursor.execute(f'PRAGMA table_info("{tn}")')
    cols = cursor.fetchall()
    col_names = [c[1] for c in cols]

    # Look for amount/money/investment columns
    for cn in col_names:
        if any(kw in cn.lower() for kw in ['amount', 'money', 'invest', 'financ', 'fund', 'capital', 'round']):
            print(f'\n>>> Found potential finance column: {tn}.{cn}')
            cursor.execute(f'SELECT DISTINCT "{cn}" FROM "{tn}" LIMIT 20')
            print(f'    Sample values: {cursor.fetchall()}')

conn.close()
