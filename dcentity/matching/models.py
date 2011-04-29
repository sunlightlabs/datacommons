from common.db.fields.uuid_field import UUIDField
from django.db import models
import uuid

class Officer(models.Model):
    id = UUIDField(primary_key=True, auto=True, default=uuid.uuid4().hex)
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=255, blank=True, null=True)
    ein = models.CharField(max_length=10)
    xml_document_id = models.IntegerField()
    organization_name = models.CharField(max_length=100)
    street = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    zip = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'guidestar_officer'


class WhiteHouseVisitor(models.Model):
    id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=64)
    middle_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

    class Meta:
        db_table = 'whitehouse_visitor'

    def build_name(self):
        return ' '.join([ x for x in [self.first_name, self.middle_name, self.last_name] if x])

    name = property(build_name)
