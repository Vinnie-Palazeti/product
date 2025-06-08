import sqlite3
from datetime import datetime, timedelta
import random

def create_and_populate_database(db_path: str = "test_metrics.db", num_days: int = 365):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop table if exists for a clean setup
    cursor.execute("DROP TABLE IF EXISTS events")

    # Create the events table
    cursor.execute("""
        CREATE TABLE events (
            date TEXT PRIMARY KEY,
            gross_revenue REAL,
            expenses REAL,
            profit REAL,
            users INTEGER,
            new_users INTEGER,
            returning_customers INTEGER,
            impressions INTEGER,
            traffic INTEGER,
            buzz REAL
        )
    """)
    
    # Populate the table with dummy daily data over the last `num_days`
    today = datetime.now().date()
    for i in range(num_days):
        current_date = today - timedelta(days=i)
        revenue = round(random.uniform(100, 10), 2)
        expenses = round(revenue * random.uniform(0.5, 0.9), 2)
        users = random.randint(100, 1000)
        new_users = random.randint(10, 20)
        returning_customers = random.randint(20, 50)
        impressions = random.randint(20, 50)
        traffic = random.randint(20, 50)
        buzz = round(random.uniform(500, 200), 2)
        
        profit = revenue - expenses
        cursor.execute(
            """
            INSERT INTO events (date, gross_revenue, expenses, profit, users, new_users, returning_customers, impressions, traffic, buzz)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (current_date.isoformat(), revenue, expenses, profit, users, new_users, returning_customers, impressions, traffic, buzz),
        )
    conn.commit()
    conn.close()
    print(
        f"Database created and populated with {num_days} days of test data at: {db_path}"
    )

# Run it
# create_and_populate_database("test_metrics.db", num_days = 2000)
