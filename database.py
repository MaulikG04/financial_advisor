import sqlite3

def create_tables():
    try:
        # Connect to SQLite database
        conn = sqlite3.connect('financial_news.db')
        c = conn.cursor()
        
        # Create articles table
        c.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            summary TEXT,
            url TEXT,
            published_at TEXT
        )
        ''')

        # Create users table
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            portfolio TEXT
        )
        ''')
        
        # Commit changes
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while creating tables: {e}")
    finally:
        # Close the connection
        conn.close()

if __name__ == '__main__':
    create_tables()
