import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.db import models
import unittest

from sql import *

class CourseModel(models.Model):
    number = models.IntegerField()
    title = models.CharField(max_length=255)

class StudentModel(models.Model):
    class Meta:
        db_table = 'lazy_students'
        
    name = models.CharField(max_length=255, db_column='studentname')
    course = models.ForeignKey(CourseModel)


class Test(unittest.TestCase):


    def test_augment(self):
        initial = {'a':1, 'b':2, 'c':3}

        self.assertEqual({}, augment({}))
        self.assertEqual(initial, augment(initial))
        self.assertEqual({'x':10,'y':11}, augment({},x=10,y=11))
        
        self.assertEqual({'a':1, 'b':2, 'c':30, 'd':40}, augment(initial, c=30, d=40))
        
        self.assertEqual({'a':1, 'b':2, 'c':3}, initial)

       
    def test_dict_union(self):
        self.assertEqual({}, dict_union())
        self.assertEqual({}, dict_union({}))
        self.assertEqual({}, dict_union({},{},{}))
        
        abc = {'a':1, 'b':2, 'c': 3}
        mn = {'m': 4, 'n':5}
        xy = {'x':6, 'y': 7}
        self.assertEqual(abc, dict_union(abc))
        self.assertEqual({'m': 4, 'n':5, 'x':6, 'y': 7}, dict_union(mn,xy))
        self.assertEqual({'a':1, 'b':2, 'c': 3, 'm': 4, 'n':5, 'x':6, 'y': 7}, dict_union(abc, mn, xy))
        
    def test_parse(self):
        i = parse_int('\\N')
        self.assertEqual(None, i)
        
        i = parse_int("123")
        self.assertEqual(123, i)
        
        f = parse_float("""\N""")
        self.assertEqual(None, f)
        
        f = parse_float("123.456")
        self.assertEqual(123.456, f)
        
        s = parse_char("\\N")
        self.assertEqual(None, s)
        
        s = parse_char('\xbb')
        self.assertEqual('\xbb', s)
        
        s = parse_char('foobar')
        self.assertEqual(u'foobar', s)
        
        d = parse_date("0000-00-00")
        self.assertEqual(d, None) 
        
        d = parse_datetime("0000-00-00 00:00:00")
        self.assertEqual(d, None) 
        
        d = parse_date("1980-05-12")
        self.assertEqual((1980, 05, 12), (d.year, d.month, d.day))
        self.assertEqual('1980-05-12', str(d))
        
        d = parse_datetime("1980-05-12 01:23:56")
        self.assertEqual((1980, 05, 12, 01, 23, 56), (d.year, d.month, d.day, d.hour, d.minute, d.second))
        self.assertEqual('1980-05-12 01:23:56', str(d))
