import sqlite3

conn = sqlite3.connect('LoginData.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS USERS (
    first_name TEXT,
    last_name TEXT,
    email TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'user'))
)
""")

# Add default accounts for testing
cursor.execute("""
INSERT OR IGNORE INTO USERS (first_name, last_name, email, password, role)
VALUES ('Admin', 'User', 'admin@gmail.com', 'adminpass', 'admin')
""")

cursor.execute("""
INSERT OR IGNORE INTO USERS (first_name, last_name, email, password, role)
VALUES ('John', 'Doe', 'user@gmail.com', 'userpass', 'user')
""")

conn.commit()
conn.close()

print("Database setup complete.")


