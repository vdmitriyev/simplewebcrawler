# coding: utf-8
#!/usr/bin/env python

import csv
import codecs
import argparse
import cStringIO
import leather

'''
USAGE:
    $ python charts_leather.py --inputcsv generated/2016-06-06-bq1dhzi.csv
'''

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

def main(input_csv):

    data_csv = input_csv

    with open(data_csv) as f:
        ur = UnicodeReader(f)
        next(ur)
        data = list(ur)[:]
        row_size  = len(data[0][:]) - 1

        for row in data:
            for index in range(row_size):
                row[index + 1] = float(row[index + 1]) if row[index + 1] is not None else None

    for value in range(3):
        data_sorted = sorted(data, key= lambda x: x[value + 1], reverse=True)
        chart = leather.Chart('Chart - CSV')
        chart.add_bars(data_sorted[:30], x=(value + 1), y=0)
        chart_output = 'generated/charts_leather_{0}.svg'.format(value)
        chart.to_svg(chart_output)
        print ('[i] following chard was generated: "{0}"'.format(chart_output))


if __name__ == '__main__':

    # setting system default encoding to the UTF-8
    import sys
    reload(sys)
    sys.setdefaultencoding('UTF8')

    # fetching input parameters
    parser = argparse.ArgumentParser(description='Diagrams with leather package')

    parser.add_argument(
        '--inputcsv',
        help='input CVS with scraped data')

    #parser.set_defaults(inputcsv=u'generated/2016-06-06-bq1dhzi.csv')

    # parse input parameters
    args = parser.parse_args()

    if not args.inputcsv:
        print ('[x] set proper input CSV file')
        exit(0)

    main(args.inputcsv)

