
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import settings
from django.db import models
import unittest

from sql_utils import django2sql_names

class CourseModel(models.Model):
    number = models.IntegerField()
    title = models.CharField(max_length=255)

class StudentModel(models.Model):
    class Meta:
        db_table = 'lazy_students'
        
    name = models.CharField(max_length=255, db_column='studentname')
    course = models.ForeignKey(CourseModel)


class Test(unittest.TestCase):

    def test_basic_model(self):
        course_names = django2sql_names(CourseModel)
        self.assertEqual('matchbox_coursemodel', course_names['coursemodel'])
        self.assertEqual('number', course_names['number'])
        self.assertEqual('title', course_names['title'])
        
    def test_custom_model(self):
        names = django2sql_names(StudentModel)
        self.assertEqual('lazy_students', names['studentmodel'])
        self.assertEqual('studentname', names['name'])
        self.assertEqual('course_id', names['course'])