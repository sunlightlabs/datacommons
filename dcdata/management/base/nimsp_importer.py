from dcdata.management.base.importer import BaseImporter
from settings import NIMSP_IMPORT_LOG_EMAIL


class BaseNimspImporter(BaseImporter):
    email_subject = 'Unhappy NIMSP Loading App'
    email_recipients = NIMSP_IMPORT_LOG_EMAIL

    def __init__(self):
        super(BaseNimspImporter, self).__init__()
