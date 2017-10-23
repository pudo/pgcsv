import click
from tabulate import tabulate

from pgcsv.csv import CSVProxy
from pgcsv.db import Database


@click.command()
@click.option('--db', envvar='DATABASE_URI')
@click.option('--encoding', default=None)
@click.option('--delimiter', default=None)
@click.option('--drop', default=False, is_flag=True)
@click.argument('table')
@click.argument('csv_file', type=click.Path(exists=True))
def main(db, encoding, delimiter, drop, table, csv_file):
    """Load a CSV file into a Postgres database."""
    proxy = CSVProxy(csv_file, encoding=encoding, delimiter=delimiter)
    db = Database(db, table, proxy)
    if drop:
        db.drop()
    print tabulate(db.headers.items(), headers=['Column', 'CSV Header'])
    db.sync()
    db.load()
