import io
from backports import csv
from normality import guess_encoding

SAMPLE_SIZE = 8192 * 10


class CSVProxy(object):

    def __init__(self, file_path, encoding=None, delimiter=None):
        if encoding is None:
            with open(file_path, 'r') as fh:
                data = fh.read(SAMPLE_SIZE)
                encoding = guess_encoding(data)

        self.fh = io.open(file_path, 'r', encoding=encoding)
        data = self.fh.read(SAMPLE_SIZE)
        dialect = csv.Sniffer().sniff(data)
        if delimiter is not None:
            dialect.delimiter = delimiter
        self.fh.seek(0)

        self.reader = iter(csv.reader(self.fh, dialect=dialect))
        self.headers = next(self.reader)
        self.count = 0

    def read(self, read_len):
        if not hasattr(self, 'buffer'):
            with io.StringIO() as out:
                csv.writer(out).writerow(self.headers)
                self.buffer = out.getvalue()

        while self.reader is not None and len(self.buffer) < read_len:
            with io.StringIO() as out:
                writer = csv.writer(out)
                try:
                    for i in range(1000):
                        row = next(self.reader)
                        writer.writerow(row)
                        self.count += 1
                        if self.count % 1000 == 0:
                            print 'Loaded %s...' % self.count
                except StopIteration:
                    self.reader = None
                self.buffer += out.getvalue()

        chunk, self.buffer = self.buffer[:read_len], self.buffer[read_len:]
        return chunk

    def close(self):
        self.fh.close()
