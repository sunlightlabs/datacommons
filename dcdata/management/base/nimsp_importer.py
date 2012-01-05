from dcdata.management.base.importer import BaseImporter

<<<<<<< HEAD
=======

class BaseNimspImporter(BaseImporter):

    def __init__(self):
        super(BaseNimspImporter, self).__init__()
>>>>>>> 51ed706... Adding a lobbying extractor script for automation. Also doing some related refactoring.

class BaseNimspImporter(BaseImporter):
    email_subject = 'Unhappy NIMSP Loading App'

    def __init__(self):
        super(BaseNimspImporter, self).__init__()
