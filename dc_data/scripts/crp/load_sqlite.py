#!/usr/bin/env python
from dcdata.contribution.sources.crp import CYCLES, FILE_TYPES, TABLE_NAMES
from dcdata.utils import ucsv
import os
import logging
import shutil
import zipfile
        
def load_sqlite(dataroot, cycles=None, file_types=None, db_per_cycle=False, indexes=False):
    
    from saucebrush.sources import CSVSource
    from saucebrush.filters import ConditionalFilter, UnicodeFilter
    from saucebrush.emitters import SqliteEmitter, DebugEmitter
    import saucebrush
    import sqlite3
    
    thispath = os.path.abspath(os.path.dirname(__file__))
    
    class FieldCountValidator(ConditionalFilter):

        def __init__(self, field_count):
            super(FieldCountValidator, self).__init__()
            self.field_count = field_count

        def test_record(self, record):
            if len(record) != self.field_count:
                self.reject_record(record, "Expected %i columns, found %i" % (self.field_count, len(record)))
                return False
            return True
    
    if not cycles:
        cycles = CYCLES
    
    if not file_types:
        file_types = FILE_TYPES     
    
    dataroot = os.path.abspath(dataroot)
    
    dest_dbpath = os.path.join(dataroot, 'sqlite', 'crp')
    if not os.path.exists(dest_dbpath):
        os.makedirs(dest_dbpath)
        
    dest_dbpath = os.path.join(dest_dbpath, 'crp.db')
        
    if not db_per_cycle:
        if os.path.exists(dest_dbpath):
            os.remove(dest_dbpath)
    
    rejected = []
    
    for cycle in cycles:
        
        # create database file
        
        dbpath = dest_dbpath
            
        if db_per_cycle:
            parts = dbpath.rsplit('.', 1)
            dbpath = "%s.%s.%s" % (parts[0], cycle, parts[1])
            if os.path.exists(dbpath):
                os.remove(dbpath)
            logging.info('creating per-cycle database %s' % dbpath)

        # create table structure
            
        conn = sqlite3.connect(dbpath)
        for stmt in open(os.path.join(thispath, 'load_sqlite_create.sql')).read().split(';'):
            conn.execute(stmt)
        conn.close()
        
        # process CSV files
        
        for ft, fields in file_types.items():
            
            table = TABLE_NAMES[ft]
            
            csvpath = os.path.join(dataroot, 'raw', 'crp', '%s%s.csv' % (ft, cycle))
            logging.info("Loading %s" % csvpath)
            infile = open(csvpath)
    
            recipe = saucebrush.run_recipe(
                CSVSource(infile, fieldnames=fields),
                FieldCountValidator(len(fields)),
                UnicodeFilter(),
                SqliteEmitter(dbpath, table),
            )
            
            infile.close()
        
            rejected.extend(recipe.rejected)
        
        if db_per_cycle and indexes:
            logging.info('adding indexes to %s' % dbpath)
            conn = sqlite3.connect(dbpath)
            for stmt in open(os.path.join(thispath, 'load_sqlite_indexes.sql')).read().split(';'):
                conn.execute(stmt)
            conn.close()
    
    if not db_per_cycle and indexes:
        logging.info('adding indexes to %s' % dbpath)
        conn = sqlite3.connect(dbpath)
        for stmt in open(os.path.join(thispath, 'load_sqlite_indexes.sql')).read().split(';'):
            conn.execute(stmt)
        conn.close()
    
    print rejected


def main():
    
    from optparse import OptionParser
    import sys
    
    usage = "usage: %prog [options]"
    
    parser = OptionParser(usage=usage)
    parser.add_option("-c", "--cycles", dest="cycles",
                      help="cycles to load ex: 90,92,08", metavar="CYCLES")
    parser.add_option("-d", "--dataroot", dest="dataroot",
                      help="path to data directory", metavar="PATH")
    parser.add_option("-i", "--indexes", action="store_true", dest="indexes", default=False,
                      help="add indexes to database")
    parser.add_option("-s", "--splitcycles", action="store_true", dest="split", default=False,
                      help="create database per cycle")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="noisy output")
    
    (options, args) = parser.parse_args()
    
    if not options.dataroot:
        parser.error("path to dataroot is required")
            
    cycles = []
    if options.cycles:
        for cycle in options.cycles.split(','):
            if len(cycle) == 4:
                cycle = cycle[2:4]
            if cycle in CYCLES:
                cycles.append(cycle)
    
    
    load_sqlite(options.dataroot, cycles=cycles, db_per_cycle=options.split, indexes=options.indexes)


if __name__ == "__main__":
    
    logging.basicConfig(level=logging.DEBUG)
    
    main()
