import sqlite3
import pandas as pd
from pathlib import Path

db_path = Path("output/electricity_metrics.db")
PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "output"
DB_PATH = OUTPUT_DIR / "electricity_metrics.db"
CSV_PATH = OUTPUT_DIR / "accepted_records.csv"

def create_database():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Accepted records not found: {CSV_PATH}")

    accepted_df = pd.read_csv(CSV_PATH)

    with sqlite3.connect(str(DB_PATH)) as conn:
        accepted_df.to_sql(
            "electricity_metrics",
            conn,
            if_exists="replace",
            index=False,
        )

    print(f"SQLite database created: {DB_PATH}")


if __name__ == "__main__":
    create_database()
    
  