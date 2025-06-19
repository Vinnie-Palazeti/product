"""
KPI Dimensions Reference
------------------------

This table will capture daily KPI measurements broken down
along each of the dimensions you described.  Each row has:

  • date       – ISO date string
  • kpi        – one of: revenue, expenses, new_users, returning_users
  • dimension  – the dimension name (e.g. “Sales Channel”)
  • category   – the category within that dimension (e.g. “online”)
  • value      – the generated metric value

"""

import sqlite3
from datetime import datetime, timedelta
import random
from tqdm import tqdm
from components.relationships import KPI_DIMENSIONS

def create_and_populate_events(db_path: str = "test_metrics.db", num_days: int = 365):
    """
    Creates an 'events' table and populates it with synthetic
    KPI data for each date, KPI, and dimension/category,
    then computes & inserts profit and total_users via SQL.
    """
    conn = sqlite3.connect(db_path)
    cur  = conn.cursor()

    # 1) Drop & recreate
    cur.execute("DROP TABLE IF EXISTS events")
    cur.execute("""
        CREATE TABLE events (
            date      TEXT,
            kpi       TEXT,
            dimension TEXT,
            category  TEXT,
            value     REAL
        )
    """)

    today      = datetime.now().date()
    start_date = today - timedelta(days=num_days - 1)
    total_rows = 0

    # 2) Populate base KPIs
    for day_offset in tqdm(range(num_days)):
        day     = start_date + timedelta(days=day_offset)
        iso_day = day.isoformat()

        for kpi, dims in KPI_DIMENSIONS.items():
            if kpi in ['profit','users']:
                continue
            for dim_name, categories in dims.items():
                for cat in categories:
                    if kpi == 'revenue':                        
                        trend = 0.5 * day_offset  # increases $0.50 per day
                        noise = random.uniform(-100, 100)  # keep random fluctuations
                        val = round(3000 + trend + noise, 2)  # base value starts at 3000                        
                    elif kpi == 'expenses':
                        val = round(random.uniform(1000, 5000), 2)
                    elif kpi == 'new_users':
                        val = random.randint(20, 200)
                    elif kpi == 'returning_users':
                        val = random.randint(10, 150)
                    else:
                        val = round(random.uniform(0, 100), 2)

                    cur.execute(
                        "INSERT INTO events (date, kpi, dimension, category, value) VALUES (?, ?, ?, ?, ?)",
                        (iso_day, kpi, dim_name, cat, val)
                    )
                    total_rows += 1

    # 3) Derive profit & total_users in SQL
    cur.executescript("""
        -- profit = sum(revenue) - sum(expenses) per day
        INSERT INTO events (date, kpi, dimension, category, value)
        SELECT
          date,
          'profit'      AS kpi,
          NULL          AS dimension,
          NULL          AS category,
          SUM(CASE WHEN kpi='revenue' THEN value ELSE 0 END)
          - SUM(CASE WHEN kpi='expenses' THEN value ELSE 0 END) AS value
        FROM events
        GROUP BY date;

        -- total_users = sum(new_users) + sum(returning_users) per day
        INSERT INTO events (date, kpi, dimension, category, value)
        SELECT
          date,
          'users' AS kpi,
          NULL          AS dimension,
          NULL          AS category,
          SUM(CASE WHEN kpi='new_users'     THEN value ELSE 0 END)
          + SUM(CASE WHEN kpi='returning_users' THEN value ELSE 0 END) AS value
        FROM events
        GROUP BY date;
    """)
    # each INSERT adds one row per date
    total_rows += 2 * num_days

    # 4) Commit & close
    conn.commit()
    conn.close()

    print(f"Populated {db_path!r} with {total_rows} event rows over {num_days} days.")

# Example: generate two years of data
create_and_populate_events(num_days=2000)