import sqlite3

# Connect (creates veriopt.db if it doesn't exist)
conn = sqlite3.connect("veriopt.db")
c = conn.cursor()

# Create the designs table
c.execute('''CREATE TABLE IF NOT EXISTS designs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    file_path TEXT,
    status TEXT,
    suggestions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

conn.commit()
conn.close()

print("✅ Database initialized with 'designs' table.")
