# Invoice Excel Data Pipeline

This project generates sample invoice workbooks and cleans them into a tabular CSV dataset.

## What is included

- `create_random_file_xlsx_looping.ipynb` generates one invoice workbook per day for the full year 2026.
- `invoice_example.xlsx` is a single styled invoice example.
- `invoices/` contains the generated daily invoice workbooks.
- `cleaning.ipynb` extracts invoice metadata and line items from the workbooks.
- `invoices_clean.csv` contains the cleaned line-item data, including payment aging categories.
- `bi_dashboard_app.py` runs a local Streamlit BI dashboard from the cleaned CSV.

## Data format

The cleaned CSV contains one row per invoice line item with these fields:

- Invoice number, invoice date, due date, and payment status
- Client name, address, and contact
- Item description, quantity, unit price, and tax rate
- Calculated line total and payment aging category

The generated invoices use a 30-day payment period and an 11% tax rate. The generator creates 365 invoice workbooks for 2026.

## Requirements

- Python 3.10 or newer
- Jupyter Notebook or JupyterLab
- `pandas`
- `openpyxl`
- `plotly`
- `streamlit`

Install the Python packages with:

```bash
python -m pip install -r requirements.txt
```

## Usage

Run the notebooks from this project directory so their relative paths work correctly:

1. Open `create_random_file_xlsx_looping.ipynb`.
2. Run the cell that generates the invoices. This creates or replaces files in `invoices/`.
3. Open `cleaning.ipynb`.
4. Run its extraction cell to create or replace `invoices_clean.csv`.
5. Start the local dashboard with `streamlit run bi_dashboard_app.py`.

The generator uses a fixed random seed, so the generated sample data is reproducible.

## Privacy note

Review all client names, addresses, contact details, email addresses, and payment information before publishing this repository. Replace any realistic-looking values with fictional data before making the repository public.

The BigQuery ingestion notebook is intentionally excluded from the public project. The included invoice data is synthetic test data.

## Project status

This is a learning and testing project for working with Excel invoice files and pandas. Validate the extracted rows and totals before using the workflow with real invoices.
