# pgcsv

The purpose of ``pgcsv`` is to make a CSV file show up in a database. To this
end, it will automatically create the table schema and COPY data. It will not
attempt to perform type inference. It will not attempt to fix up your CSV
file (the file is assumed to be readable as UTF-8 with the first row containing
column headers).

## Usage

```bash
$ pip install pgcsv
$ pgcsv --db postgresql://localhost/database new_table csv_file.csv
```
