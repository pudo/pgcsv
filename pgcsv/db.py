from psycopg2 import connect
from psycopg2.sql import SQL, Identifier, Literal, Composed
from collections import OrderedDict
from itertools import count

from pgcsv.util import normalize_column


class Database(object):

    def __init__(self, uri, table, proxy):
        self.conn = connect(uri)
        self.table = normalize_column(table)
        self.proxy = proxy

    @property
    def headers(self):
        if not hasattr(self, '_headers'):
            self._headers = OrderedDict()
            for name in self.proxy.headers:
                normalized = normalize_column(name)
                if normalized is None or not len(normalized):
                    normalized = 'column'
                column = normalized
                for i in count(2):
                    if column not in self._headers:
                        break
                    column = '%s_%s' % (normalized, i)
                self._headers[column] = name
        return self._headers

    def drop(self):
        with self.conn.cursor() as cursor:
            stmt = SQL('DROP TABLE IF EXISTS {};')
            stmt = stmt.format(Identifier(self.table))
            # print stmt.as_string(cursor)
            cursor.execute(stmt)
        self.conn.commit()

    def sync(self):
        with self.conn.cursor() as cursor:
            stmt = SQL("CREATE TABLE IF NOT EXISTS {} ();")
            stmt = stmt.format(Identifier(self.table))
            # print stmt.as_string(cursor)
            cursor.execute(stmt)

            stmt = SQL("SELECT column_name FROM "
                       "information_schema.columns "
                       "WHERE table_name = %s;")  # noqa
            cursor.execute(stmt, (self.table,))
            columns = [c[0] for c in cursor.fetchall()]
            columns = [c.decode(self.conn.encoding) for c in columns]
            for column, label in self.headers.items():
                if column not in columns:
                    stmt = SQL("ALTER TABLE {} ADD COLUMN {} TEXT;")
                    stmt = stmt.format(Identifier(self.table),
                                       Identifier(column))
                    # print stmt.as_string(cursor)
                    cursor.execute(stmt)
                stmt = SQL("COMMENT ON COLUMN {}.{} IS {};")
                stmt = stmt.format(Identifier(self.table),
                                   Identifier(column),
                                   Literal(label))
                cursor.execute(stmt)
        self.conn.commit()

    def load(self):
        with self.conn.cursor() as cursor:
            headers = self.headers.keys()
            stmt = SQL("COPY {} ({}) FROM STDIN WITH CSV HEADER NULL AS ''")
            columns = Composed([Identifier(c) for c in headers])
            columns = columns.join(', ')
            stmt = stmt.format(Identifier(self.table), columns)
            # print stmt.as_string(cursor)
            cursor.copy_expert(stmt, self.proxy)
        self.conn.commit()
