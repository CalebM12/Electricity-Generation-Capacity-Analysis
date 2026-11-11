# Canadian Electricity Data Conversion and Validation

## Overview

This project explores how to profile, standardize, and validate Canadian electricity generation and capacity data. It uses two CSV datasets and aims to convert them into a consistent structure that is easier to validate and use for downstream analysis.

The project is designed to demonstrate data-conversion practices relevant to utility data work, including source-data profiling, transformation, data-quality handling, and reconciliation. It is a portfolio demonstration using electricity metrics—not a utility billing or customer-data migration.


## Data

The repository includes:

| File | Description |
|---|---|
| `data-files/electricity-generation-dataset.csv` | Electricity generation by region, source, and year. Values use `GW.h`. |
| `data-files/electricity-capacity-dataset.csv` | Electricity capacity by region, source, and year. Values use `MW`. |
| `data-files/electricity-capacity-guide.csv` | Guide describing fields or values in the capacity data. |

The generation dataset contains 1,344 rows and covers 2005–2016. The capacity dataset contains 2,688 rows, including blank data that will be profiled and handled according to documented rules.

The datasets contain fields such as region, energy source, year, value, and unit. Generation and capacity are different measures and their units are preserved separately.

 [https://open.canada.ca/data/en/dataset/2cdf43fc-d4aa-4604-9f21-29777d955810](Open Canada dataset, Electricity generation and capacity in Canada)



## Target Structure

The planned standardized output will include fields such as:

| Field | Description | Example |
|---|---|---|
| `measure_type` | Identifies generation or capacity | `generation` |
| `region` | Region from the source data | `Canada` |
| `source` | Electricity source | `Hydro` |
| `year` | Reporting year | `2005` |
| `value` | Numeric measure | `358386.9629` |
| `unit` | Unit from the source | `GW.h` |
| `source_file` | Original input file | `electricity-generation-dataset.csv` |
| `source_row` | Original row number for traceability | `2` |

The exact target schema and mapping rules will be documented before they are implemented.




## Repository Contents

```text
.
├── data-files/
│   ├── electricity-capacity-dataset.csv
│   ├── electricity-capacity-guide.csv
│   └── electricity-generation-dataset.csv
├── notebook.ipynb
└── README.md
