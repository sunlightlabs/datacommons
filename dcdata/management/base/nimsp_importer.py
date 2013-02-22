from dcdata.management.base.importer import BaseImporter
from django.conf import settings


class BaseNimspImporter(BaseImporter):
    email_subject = 'Unhappy NIMSP Loading App'
    email_recipients = settings.LOGGING_EMAIL['recipients']

    def __init__(self):
        super(BaseNimspImporter, self).__init__()
