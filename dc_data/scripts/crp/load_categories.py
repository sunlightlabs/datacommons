#!/usr/bin/env python
from saucebrush.sources import CSVSource
from saucebrush.emitters import DebugEmitter, SqliteEmitter
import saucebrush
import sqlite3
import logging
import os

FIELDS = ('catcode','catname','catorder','industry','sector','sector_long')

def load_sqlite(dataroot, indexes=False):
    
    dataroot = os.path.abspath(dataroot)
    dbpath = os.path.join(dataroot, 'sqlite', 'crp', 'catcodes.db')
    
    conn = sqlite3.connect(dbpath)
    conn.execute("""DROP TABLE IF EXISTS catcode""")
    conn.close()
    
    csvpath = os.path.join(dataroot, 'raw', 'crp', 'CRP_Categories.txt')
    saucebrush.run_recipe(
        CSVSource(open(csvpath), fieldnames=FIELDS, skiprows=8, delimiter='\t'),
        #DebugEmitter(),
        SqliteEmitter(dbpath, 'catcode', fieldnames=FIELDS, replace=True),
    )
    
    if indexes:
        logging.info('adding indexes to %s' % dbpath)
        conn = sqlite3.connect(dbpath)
        conn.execute("""CREATE INDEX IF NOT EXISTS catcode_catcode_idx ON catcode (catcode)""")
        conn.execute("""CREATE INDEX IF NOT EXISTS catcode_catname_idx ON catcode (catname)""")
        conn.execute("""CREATE INDEX IF NOT EXISTS catcode_catorder_idx ON catcode (catorder)""")
        conn.execute("""CREATE INDEX IF NOT EXISTS catcode_industry_idx ON catcode (industry)""")
        conn.execute("""CREATE INDEX IF NOT EXISTS catcode_sector_idx ON catcode (sector)""")
        conn.close()

def main():

    from optparse import OptionParser
    import sys

    usage = "usage: %prog [options]"

    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--dataroot", dest="dataroot",
                      help="path to data directory", metavar="PATH")
    parser.add_option("-i", "--indexes", action="store_true", dest="indexes", default=False,
                      help="add indexes to database")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="noisy output")

    (options, args) = parser.parse_args()

    if not options.dataroot:
        parser.error("path to dataroot is required")

    load_sqlite(options.dataroot, indexes=options.indexes)


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    main()
