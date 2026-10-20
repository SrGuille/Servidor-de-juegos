import argparse
import csv
import sqlite3
from pathlib import Path


TABLES = {
    "Coins_evolutions": "servidor_coins_evolution",
    "Players": "servidor_player",
    "Prizes": "servidor_prize",
    "Prizes_evolutions": "servidor_prizes_evolution",
}


def export_table_to_csv(connection: sqlite3.Connection, table_name: str, output_file: Path) -> int:
    cursor = connection.cursor()

    # Read column names from the table schema.
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    if not columns_info:
        raise ValueError(f"Table not found or has no columns: {table_name}")

    column_names = [column[1] for column in columns_info]

    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    with output_file.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(column_names)
        writer.writerows(rows)

    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export selected SQLite tables to CSV (one CSV per table)."
    )
    parser.add_argument(
        "--db-path",
        default="db.sqlite3",
        help="Path to SQLite database file (default: db.sqlite3)",
    )
    parser.add_argument(
        "--out-dir",
        default="csv_export",
        help="Output directory for CSV files (default: csv_export)",
    )
    args = parser.parse_args()

    db_path = Path(args.db_path)
    out_dir = Path(args.out_dir)

    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    out_dir.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)
    try:
        print(f"Exporting tables from: {db_path}")
        print(f"Output directory: {out_dir.resolve()}")

        for csv_name, table_name in TABLES.items():
            output_file = out_dir / f"{csv_name}.csv"
            exported_rows = export_table_to_csv(connection, table_name, output_file)
            print(f"- {table_name} -> {output_file.name} ({exported_rows} rows)")

        print("Export completed successfully.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
