"""
This code was taken from the Python documentation.
http://docs.python.org/library/csv.html
"""

import csv, codecs, cStringIO
import unicodedata

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

class UnicodeDictReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, fieldnames=None, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.DictReader(f, fieldnames=fieldnames, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return {k: unicode(v, "utf-8") for k, v in row.iteritems()}

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

class UnicodeDictWriter(object):
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """
 
    def __init__(self, f, fieldnames, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.fieldnames = fieldnames
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoding = encoding
        self.encoder = codecs.getincrementalencoder(self.encoding)()
        
    def writeheader(self):
        self.writer.writerow(self.fieldnames)

    def mask_row(self,row):
        return row

    def writerow(self, row):
        self.writer.writerow(self.mask_row(row))
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)
 
    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
    
 
class AsciiIgnoreDictWriter(UnicodeDictWriter):
    """
    A CSV writer which will write rows to CSV file "f",
    where the source data is in the encoding
    """

    def __init__(self, *args, **kwargs):
        kwargs['encoding'] = 'ascii'
        super(AsciiIgnoreDictWriter, self).__init__(*args,**kwargs)
    
    def mask_row(self,row):
        return [row[x].encode("utf-8").decode('utf-8').encode('ascii','ignore') if (isinstance(row[x],str) or isinstance(row[x],unicode)) else row[x] for x in self.fieldnames]
 
class AsciiNormalizedDictWriter(UnicodeDictWriter):
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """
 
    def __init__(self, *args, **kwargs):
        kwargs['encoding'] = 'ascii'
        super(AsciiNormalizedDictWriter, self).__init__(*args,**kwargs)
    
    def mask_row(self,row):
        return [unicodedata.normalize('NFKD', row[x].encode("utf-8").decode('utf-8')).encode('ascii','ignore') if (isinstance(row[x],str) or isinstance(row[x],unicode)) else row[x] for x in self.fieldnames]
 
