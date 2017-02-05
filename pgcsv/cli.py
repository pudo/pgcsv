import os
import re
import click
import psycopg2
# from psycopg2.sql import SQL
from unicodedata import category
from collections import OrderedDict
from itertools import count
from unicodecsv import reader, Sniffer
from tabulate import tabulate

CREATE_STMT = u"""CREATE TABLE IF NOT EXISTS {} ({});"""
ALTER_STMT = u"""ALTER TABLE {} ADD COLUMN "{}" TEXT;"""
COMMENT_STMT = u"""COMMENT ON COLUMN {}."{}" IS %s;"""
SCHEMA_STMT = u"""SELECT column_name FROM information_schema.columns WHERE table_name = %s; """  # noqa
COPY_STMT = u"""COPY {} ({}) FROM STDIN WITH CSV HEADER NULL AS '' DELIMITER AS '{}'"""  # noqa


def normalize_column(name, sep='_'):
    name = name.lower()
    characters = []
    for character in name:
        cat = category(character)[:1]
        if cat in ['C', 'M', 'S']:
            continue
        if cat not in ['L', 'N']:
            character = ' '
        characters.append(character)
    name = u''.join(characters)
    name = re.sub(r'\s+', ' ', name).strip(' ')
    return name.replace(' ', sep)


def normalize_headers(names):
    headers = OrderedDict()
    for name in names:
        normalized = normalize_column(name)
        if normalized is None or not len(normalized):
            normalized = 'column'
        column = normalized
        for i in count(2):
            if column not in headers:
                break
            column = '%s_%s' % (normalized, i)
        headers[column] = name

    print tabulate(headers.items(), headers=['Column', 'CSV Header'])
    return headers


def adapt_schema(conn, table_name, headers):
    with conn.cursor() as cursor:
        # TODO: fix this when psycopg2 2.7 comes out.
        # columns = [sql.Identifier(c) for c in headers.keys()]
        # columns = sql.SQL(', ').join(columns)
        columns = ['"%s" TEXT' % c for c in headers.keys()]
        columns = ', '.join(columns)
        query = CREATE_STMT.format(table_name, columns)
        cursor.execute(query)

        cursor.execute(SCHEMA_STMT, (table_name,))
        columns = [c[0].decode(conn.encoding) for c in cursor.fetchall()]
        for column, label in headers.items():
            if column not in columns:
                query = ALTER_STMT.format(table_name, column)
                cursor.execute(query)
            query = COMMENT_STMT.format(table_name, column)
            cursor.execute(query, (label, ))

        conn.commit()
    return headers


def load_data(fh, conn, dialect, table_name, headers):
    fh.seek(0)
    with conn.cursor() as cursor:
        columns = ['"%s"' % c for c in headers.keys()]
        columns = ', '.join(columns)
        query = COPY_STMT.format(table_name, columns, dialect.delimiter)
        cursor.copy_expert(query, fh, size=8192 * 10)
    conn.commit()


@click.command()
@click.option('--db', envvar='DATABASE_URI')
@click.argument('table_name')
@click.argument('csv_file')
def main(db, table_name, csv_file):
    """Load a CSV file into a Postgres database."""
    if not os.path.isfile(csv_file):
        raise click.ClickException("CSV file does not exist!")

    conn = psycopg2.connect(db)

    with open(csv_file, 'r') as fh:
        dialect = Sniffer().sniff(fh.read(8192 * 10))
        fh.seek(0)
        read = reader(fh, dialect=dialect)
        headers = normalize_headers(next(read))
        adapt_schema(conn, table_name, headers)
        load_data(fh, conn, dialect, table_name, headers)
