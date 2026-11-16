import sqlite3

import pandas as pd

conn = sqlite3.connect("output/electricity_metrics.db")

queries = [
    """
    SELECT year, source, SUM(value) AS total_generation
    FROM electricity_metrics
    WHERE measure_type = 'generation'
    GROUP BY year, source
    ORDER BY year, source
    LIMIT 10;
    """,
    """
    SELECT region, source, SUM(value) AS total_capacity
    FROM electricity_metrics
    WHERE measure_type = 'capacity'
    AND year = 2016
    GROUP BY region, source
    ORDER BY total_capacity DESC
    LIMIT 10;
    """
]

for query in queries:
    print("\nQUERY:\n", query)
    print(pd.read_sql_query(query, conn).head())

conn.close()