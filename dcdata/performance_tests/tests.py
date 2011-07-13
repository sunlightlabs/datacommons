
from time import time
import subprocess
import logging
from nose.plugins.skip import Skip, SkipTest

from django.test.testcases import TransactionTestCase
from django.db.transaction import commit_manually
from django.db import connections, transaction

from models import DummyModel

THOUSAND = 1000
MILLION = THOUSAND * THOUSAND

NUM_SAMPLES = 10
ITERATIONS_PER_SAMPLE = 10 * THOUSAND
COMMIT_SIZE = 10 * THOUSAND

SQL_INSERT_STMT = 'insert into performance_tests_dummymodel values (%s, %s, %s, %s, %s)'


class InsertPerformanceTests(TransactionTestCase):
    
    def get_row(self, i):
        return (str(i), str(i), str(i), str(i))
    
    def setUp(self):
        self.cursor = connections['default'].cursor()

    def tearDown(self):
        transaction.rollback()
        
    def django_insert(self, i):
        DummyModel.objects.create(a = str(i), b = str(i), c = str(i), d = str(i))
        
    def sql_insert(self, i):
        self.cursor.execute(SQL_INSERT_STMT, [i, str(i), str(i), str(i), str(i)])    
        
    def sql_insertmany(self, i, chunk_size = THOUSAND):
        self.inserts.append([i, str(i), str(i), str(i), str(i)])
        
        if i % chunk_size == 0:
            self.cursor.executemany(SQL_INSERT_STMT, self.inserts)
            self.inserts = list()
            
    def sql_dump_insert(self, i, out_file):
        out_file.write(SQL_INSERT_STMT % (i, str(i), str(i), str(i), str(i)))
        out_file.write(';\n')
        
    def commit_sql_dump(self, out_file):
        out_file.write('commit;\n')
        out_file.write('begin;\n')
        out_file.flush()
            
        
    def testDjangoInserts(self):
        raise SkipTest
        logging.info('Running Django insert tests...')
        
        self.run_inserts(self.django_insert, transaction.commit)
        
    def testSQLInserts(self):
        raise SkipTest
        logging.info('Running SQL insert tests...')
        
        self.run_inserts(self.sql_insert, transaction.commit)
        
    def testSQLManyInserts(self):
        raise SkipTest
        logging.info('Running SQL many-insert tests...')
        
        self.inserts = list()
        
        self.run_inserts(self.sql_insertmany, transaction.commit)
        
    def testSQLDumpAndLoadInserts(self):
        raise SkipTest
        logging.info('Running SQL dump and load tests...')
        
        dump_file = open('/tmp/performance_tests.dump', 'w')
        dump_file.write('begin;\n')
        
        self.run_inserts((lambda i: self.sql_dump_insert(i, dump_file)), (lambda: self.commit_sql_dump(dump_file)))
        
        dump_file.close()
        
        start_time = time()
        subprocess.call(['psql', '-q', '-f', '/tmp/performance_tests.dump', 'test_datacommons'])
        end_time = time()
        
        logging.info('Load to psql took %f seconds.' % (end_time - start_time))
        

    @commit_manually   
    def run_inserts(self, insert_func, commit_func):
        start_time = time()
        
        i = 0
        last_time = time()
        
        while i < ITERATIONS_PER_SAMPLE * NUM_SAMPLES:
            i += 1
            
            insert_func(i)
            
            if i % COMMIT_SIZE == 0:
                commit_func()
            
            if i % ITERATIONS_PER_SAMPLE == 0:
                new_time = time()
                logging.info('Last %d inserts out of %d total inserts took %f seconds.' % (ITERATIONS_PER_SAMPLE, i, new_time - last_time))
                last_time = new_time
                
        logging.info('Total time was %f seconds.' % (time() - start_time))
        
