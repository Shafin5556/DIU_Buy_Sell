import sqlite3

def add_is_admin_column():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0')
        conn.commit()

add_is_admin_column()
