import io
from backports import csv
from normality import guess_encoding

SAMPLE_SIZE = 8192 * 10


def open_csv(file_path, encoding=None, delimiter=None):
    if encoding is None:
        with io.open(file_path, 'rb') as fh:
            data = fh.read(SAMPLE_SIZE)
            encoding = guess_encoding(data)

    fh = io.open(file_path, 'r', encoding=encoding)
    if delimiter is None:
        data = fh.read(SAMPLE_SIZE)
        dialect = csv.Sniffer().sniff(data)
        delimiter = dialect.delimiter
        fh.seek(0)

    reader = csv.reader(fh, delimiter=delimiter)
    headers = []
    for row in reader:
        headers = row
        break
    fh.seek(0)
    return fh, delimiter, headers
