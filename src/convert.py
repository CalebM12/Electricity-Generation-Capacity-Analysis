from pathlib import Path

import json
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data-files"
OUTPUT_DIR = PROJECT_DIR / "output"

ELECTRICITY_COLUMNS = [
    "measure_type",
    "region",
    "source",
    "year",
    "value",
    "unit",
    "source_file",
]


def prepare_dataset(filename, measure_type):
    file_path = DATA_DIR / filename

    if not file_path.is_file():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    df = pd.read_csv(file_path)

    required_columns = {"Region", "Source", "Year", "Data", "Unit"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"{filename} is missing columns: {sorted(missing_columns)}")

    df = df.rename(
        columns={
            "Region": "region",
            "Source": "source",
            "Year": "year",
            "Data": "value",
            "Unit": "unit",
        }
    )

    df["measure_type"] = measure_type
    df["source_file"] = filename

    return df[ELECTRICITY_COLUMNS]


def validate_records(combined):
    required_fields = ["region", "source", "year", "value", "unit"]
    missing_columns = set(required_fields + ["measure_type"]) - set(combined.columns)
    if missing_columns:
        raise ValueError(f"Input data is missing columns: {sorted(missing_columns)}")

    blank = combined[required_fields].isna() | (
        combined[required_fields]
        .astype("string")
        .apply(lambda column: column.str.strip().eq(""))
        .fillna(False)
    )

    checks = pd.DataFrame(index=combined.index)
    entirely_blank = blank.all(axis=1)
    checks["all_source_fields_blank"] = entirely_blank

    valid_sources = [
        "Hydro", "Wind", "Biomass", "Solar", "Nuclear",
        "Coal", "Natural Gas", "Oil and Diesel",
    ]
    valid_regions = [
        "Canada", "BC", "AB", "SK", "MB", "ON", "QC", "NB", "NS", "NL",
        "PE", "YT", "NT", "NU",
    ]
    expected_units = combined["measure_type"].map({
        "capacity": "MW",
        "generation": "GW.h",
    })

    for column in required_fields:
        checks[f"missing_{column}"] = blank[column] & ~entirely_blank

    years = pd.to_numeric(combined["year"], errors="coerce")
    values = pd.to_numeric(combined["value"], errors="coerce")

    checks["invalid_year"] = ~blank["year"] & years.isna()
    checks["year_out_of_range"] = years.notna() & ~years.between(2005, 2016)
    checks["non_integer_year"] = years.notna() & years.mod(1).ne(0)
    checks["invalid_value"] = ~blank["value"] & values.isna()
    checks["invalid_source"] = (
        ~blank["source"] & ~combined["source"].isin(valid_sources)
    )
    checks["invalid_unit"] = (
        ~blank["unit"] & combined["unit"].ne(expected_units)
    )
    checks["invalid_measure_type"] = ~combined["measure_type"].isin(
        ["capacity", "generation"]
    )
    checks["invalid_region"] = (
        ~blank["region"] & ~combined["region"].isin(valid_regions)
    )

    reasons = checks.apply(
        lambda row: "; ".join(row.index[row]),
        axis=1,
    )

    initially_accepted = combined.loc[reasons.eq("")].copy()
    initially_accepted["year"] = years.loc[initially_accepted.index].astype("int64")
    initially_accepted["value"] = values.loc[initially_accepted.index]

    key_columns = ["measure_type", "region", "source", "year"]
    duplicate_mask = initially_accepted.duplicated(
        subset=key_columns,
        keep=False,
    )
    duplicate_indices = initially_accepted.index[duplicate_mask]
    checks["duplicate_target_key"] = False
    checks.loc[duplicate_indices, "duplicate_target_key"] = True
    reasons = checks.apply(
        lambda row: "; ".join(row.index[row]),
        axis=1,
    )

    rejected_mask = reasons.ne("")
    accepted = combined.loc[~rejected_mask].copy()
    rejected = combined.loc[rejected_mask].copy()
    rejected["rejection_reason"] = reasons.loc[rejected_mask]
    accepted["year"] = years.loc[accepted.index].astype("int64")
    accepted["value"] = values.loc[accepted.index]

    duplicate_keys_df = (
        initially_accepted.loc[duplicate_mask, key_columns]
        .drop_duplicates()
    )
    duplicate_target_keys = [
        {
            "measure_type": row.measure_type,
            "region": row.region,
            "source": row.source,
            "year": int(row.year),
        }
        for row in duplicate_keys_df.itertuples(index=False)
    ]

    counts_balance = len(combined) == len(accepted) + len(rejected)
    if not counts_balance:
        raise RuntimeError("Reconciliation failed: input rows do not balance.")

    report = {
        "input_rows": len(combined),
        "accepted_rows": len(accepted),
        "rejected_rows": len(rejected),
        "counts_balance": "Pass" if counts_balance else "Fail",
        "rejected_by_reason": rejected["rejection_reason"].value_counts().to_dict(),
        "duplicate_target_key_rows": int(duplicate_mask.sum()),
        "duplicate_target_key_groups": len(duplicate_target_keys),
        "duplicate_target_keys": duplicate_target_keys,
    }
    return accepted, rejected, report


def main():
    electricity_capacity = prepare_dataset(
        "electricity-capacity-dataset.csv",
        "capacity",
    )
    electricity_generation = prepare_dataset(
        "electricity-generation-dataset.csv",
        "generation",
    )
    combined = pd.concat(
        [electricity_capacity, electricity_generation],
        ignore_index=True,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT_DIR / "combined_unclean_electricity.csv", index=False)

    accepted, rejected, report = validate_records(combined)
    accepted.to_csv(OUTPUT_DIR / "accepted_records.csv", index=False)
    rejected.to_csv(OUTPUT_DIR / "rejected_records.csv", index=False)

    report_path = OUTPUT_DIR / "reconciliation.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Reconciliation report saved to {report_path}")


if __name__ == "__main__":
    main()