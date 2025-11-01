# Import the provided Excel file

This small helper reads `Volcano Data.xlsx` in the repository, prints a preview and writes a CSV to `data/output.csv`.

Requirements
- Python 3.8+
- Install Python packages listed in `requirements.txt`.

PowerShell (Windows) quick start

```powershell
cd 'C:\Users\Hp\.vscode\Volcanos\Volcanos'
python -m pip install -r requirements.txt
python import_excel.py -i 'Volcano Data.xlsx' -o data/output.csv --preview 10
```

Options
- `-i, --input` : path to Excel file (defaults to `Volcano Data.xlsx`)
- `-s, --sheet` : sheet name or index (default: first sheet)
- `-o, --output`: output CSV path (default: `data/output.csv`)
- `--to-json`  : also write JSON file alongside CSV
# Volcanos