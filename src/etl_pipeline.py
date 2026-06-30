from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "sample_synthetic_data.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
DB_PATH = OUTPUT_DIR / "operations.sqlite"


def extract() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH, parse_dates=["date"], keep_default_na=False)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()
    clean = clean.drop_duplicates(subset=["record_id"])
    numeric_cols = ["contacts", "resolved_contacts", "escalations", "aht_seconds", "csat_score"]
    for col in numeric_cols:
        clean[col] = pd.to_numeric(clean[col], errors="coerce")
    clean = clean.dropna(subset=numeric_cols + ["date", "region", "channel"])
    clean = clean[clean["contacts"] > 0]
    clean["resolution_rate"] = clean["resolved_contacts"] / clean["contacts"]
    clean["date"] = clean["date"].dt.date.astype(str)
    return clean


def load(clean: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        clean.to_sql("operations_clean", conn, if_exists="replace", index=False)


def run_queries() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        summary = pd.read_sql_query(
            '''
            SELECT region, channel,
                   ROUND(AVG(csat_score), 2) AS avg_csat,
                   ROUND(SUM(resolved_contacts) * 1.0 / SUM(contacts), 3) AS resolution_rate
            FROM operations_clean
            GROUP BY region, channel
            ORDER BY region, channel
            ''',
            conn,
        )
    print(summary.to_string(index=False))


def main() -> None:
    raw = extract()
    clean = transform(raw)
    load(clean)
    print(f"Loaded {len(clean)} clean rows into {DB_PATH}")
    run_queries()


if __name__ == "__main__":
    main()
