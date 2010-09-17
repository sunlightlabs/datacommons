from unittest2 import TestCase
from django.http import HttpRequest
from dcapi.aggregates.contributions.handlers import SparklineByPartyHandler
from django.db import DatabaseError
import uuid

class TestSparklineByPartyHandler(TestCase):
    def test_read(self):
        handler = SparklineByPartyHandler()
        request = HttpRequest()
        request.GET['cycle'] = -1
        # we don't have the database table to call on, but we can make sure our
        # code can get that far (i.e. it runs)
        with self.assertRaises(DatabaseError):
            handler.read(request, entity_id=uuid.UUID('ABCDE'))


