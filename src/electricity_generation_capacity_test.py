import pandas as pd
from convert import validate_records


def make_sample_data(**overrides):
    record = {
        "measure_type": "generation",
        "region": "Canada",
        "source": "Hydro",
        "year": 2005,
        "value": 1.5,
        "unit": "GW.h",
        "source_file": "sample.csv",
    }
    record.update(overrides)
    return pd.DataFrame([record])


sample_data = {
    "invalid_year": make_sample_data(year="not-a-year"),
    "year_out_of_range": make_sample_data(year=2017),
    "non_integer_year": make_sample_data(year=2005.5),
    "invalid_value": make_sample_data(value="not-a-number"),
    "invalid_source": make_sample_data(source="Golden Sun"),
    "invalid_unit": make_sample_data(unit="MW"),
    "invalid_measure_type": make_sample_data(measure_type="transmission"),
    "invalid_region": make_sample_data(region="North Pole"),
    "entirely_blank_row": make_sample_data(
        region="",
        source="",
        year="",
        value="",
        unit="",
    ),
    "duplicate_target_key": pd.concat(
        [make_sample_data(), make_sample_data()],
        ignore_index=True,
    ),
    "valid": make_sample_data(),
}

def test_invalid_year_is_rejected():
    accepted, rejected, report = validate_records(sample_data["invalid_year"])

    assert len(accepted) == 0
    assert len(rejected) == 1
    assert "invalid_year" in rejected.iloc[0]["rejection_reason"]
    
    
def test_year_out_of_range_is_rejected():
    accepted, rejected, report = validate_records(sample_data["year_out_of_range"])

    assert len(accepted) == 0
    assert len(rejected) == 1
    assert "year_out_of_range" in rejected.iloc[0]["rejection_reason"]
    
    
    
def test_non_integer_year_is_rejected():
    accepted, rejected, report = validate_records(sample_data["non_integer_year"])

    assert len(accepted) == 0
    assert len(rejected) == 1
    assert "non_integer_year" in rejected.iloc[0]["rejection_reason"]
    
def test_invalid_value_is_rejected():
    accepted, rejected, report = validate_records(sample_data["invalid_value"])

    assert len(accepted) == 0
    assert len(rejected) == 1
    assert "invalid_value" in rejected.iloc[0]["rejection_reason"]

def test_invalid_source_is_rejected():
    accepted, rejected, report = validate_records(sample_data["invalid_source"])

    assert len(accepted) == 0
    assert len(rejected) == 1
    assert "invalid_source" in rejected.iloc[0]["rejection_reason"]

def test_invalid_unit_is_rejected():
    accepted, rejected, report = validate_records(sample_data["invalid_unit"])

    assert len(accepted) == 0
    assert len(rejected) == 1
    assert "invalid_unit" in rejected.iloc[0]["rejection_reason"]
    
def test_invalid_measure_type_is_rejected():
    accepted, rejected, report = validate_records(sample_data["invalid_measure_type"])

    assert len(accepted) == 0
    assert len(rejected) == 1
    assert "invalid_measure_type" in rejected.iloc[0]["rejection_reason"]

def test_invalid_region_is_rejected():
    accepted, rejected, report = validate_records(sample_data["invalid_region"])

    assert len(accepted) == 0
    assert len(rejected) == 1
    assert "invalid_region" in rejected.iloc[0]["rejection_reason"]

def test_entirely_blank_row_is_rejected():
    accepted, rejected, report = validate_records(sample_data["entirely_blank_row"])

    assert len(accepted) == 0
    assert len(rejected) == 1
    assert "all_source_fields_blank" in rejected.iloc[0]["rejection_reason"]
    
def test_duplicate_target_key_is_rejected():
    accepted, rejected, report = validate_records(sample_data["duplicate_target_key"])

    assert len(accepted) == 0
    assert len(rejected) == 2
    assert "duplicate_target_key" in rejected.iloc[0]["rejection_reason"]
    assert "duplicate_target_key" in rejected.iloc[1]["rejection_reason"]
    
def test_reconciliation_report_contains_expected_fields():
    accepted, rejected, report = validate_records(sample_data["valid"])

    expected_fields = [
        "input_rows",
        "accepted_rows",
        "rejected_rows",
        "counts_balance",
        "rejected_by_reason",
        "duplicate_target_key_rows",
        "duplicate_target_key_groups",
        "duplicate_target_keys"
    ]

    for field in expected_fields:
        assert field in report
        
    