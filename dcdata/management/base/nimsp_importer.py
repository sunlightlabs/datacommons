from dcdata.management.base.importer import BaseImporter


class BaseNimspImporter(BaseImporter):
    email_subject = 'Unhappy NIMSP Loading App'

    def __init__(self):
        super(BaseNimspImporter, self).__init__()
