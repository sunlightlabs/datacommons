import os
import os.path
import fnmatch
import time
import datetime

from dcdata.utils.log            import set_up_logger
from django.core.management.base import BaseCommand, CommandError
from optparse                    import make_option
from django.conf                 import settings


class BaseImporter(BaseCommand):

    IN_DIR       = None # '/home/datacommons/data/auto/nimsp/raw/IN'
    DONE_DIR     = None # '/home/datacommons/data/auto/nimsp/raw/DONE'
    REJECTED_DIR = None # '/home/datacommons/data/auto/nimsp/raw/REJECTED'
    OUT_DIR      = None # '/home/datacommons/data/auto/nimsp/denormalized/IN'
    FILE_PATTERN = None # bash-style, ala '*.sql'

    email_subject = 'Unhappy Loading App'
    email_recipients = settings.LOGGING_EMAIL['recipients']

    # initializing this here so that tests which don't call handle() don't fail
    dry_run = None

    option_list = BaseCommand.option_list + (
        make_option('--dry-run', '-d',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Do a test run of the command, only printing what would be done.'
        ),
    )


    def __init__(self):
        super(BaseImporter, self).__init__()
        self.class_name = self.__class__.__name__
        self.module_name = self.__module__.split('.')[-1]
        self.log_path = settings.LOGGING_DIRECTORY
        self.log = set_up_logger(self.module_name, self.log_path, self.email_subject, email_recipients=self.email_recipients)
        self.pid_file_path = os.path.join(settings.TMP_DIRECTORY, self.module_name)


    def handle(self, *args, **options):
        """
            Will run the do_for_file operation from a subclass on every
            eligible file found in the IN_DIR, or will log what it would
            do if the dry_run option is specified.
        """

        self.die_if_already_running()
        self.set_pid_file()

        self.log.info('Starting {0}'.format(self.class_name))

        self.dry_run = options['dry_run']

        if not self.dry_run:
            self.do_first()

        file_func = self.dry_run_for_file if self.dry_run else self.do_for_file

        self.main_loop(file_func)

        self.destroy_pid_file()

        self.log.info('Finished.')


    def main_loop(self, file_func):
        for file_path in self.find_eligible_files():
            if not os.path.exists(file_path):
                continue
            else:
                try:
                    file_func(file_path)
                except:
                    self.log.exception("Unexpected error:")
                    self.reject_file(file_path)
                    break


    # define this in the derived classes
    def do_for_file(self, file_path):
        """
            The meat of the operation happens here.

            Takes the input file basename and its location/path as arguments.
        """
        pass


    # define this in the derived classes
    def dry_run_for_file(self, file, file_path):
        pass


    # define this (only if necessary) in the derived classes
    def do_first(self):
        pass


    def find_eligible_files(self):
        """
            Goes through the IN_DIR and finds files matching the FILE_PATTERN to act on
        """
        files = os.listdir(self.IN_DIR)

        if len(files) > 0:
            for file in files:
                file_path = os.path.join(self.IN_DIR, file)
                self.log.info('Found file {0}'.format(file))
                if fnmatch.fnmatch(file, self.FILE_PATTERN):
                    if self.file_has_not_been_written_to_for_over_a_minute(file_path):
                        yield file_path
                    else:
                        self.log.info('File last modified time is too recent. Skipping.')
                else:
                    self.log.warning('{0} doesn\'t match the file pattern ({1}). Rejecting.'.format(file, self.FILE_PATTERN))
                    self.reject_file(file)
        else:
            self.log.info('No files found.')


    def reject_file(self, path):
        if not self.dry_run:
            name = os.path.basename(path)
            os.rename(os.path.join(self.IN_DIR, name), os.path.join(self.REJECTED_DIR, name))


    def archive_file(self, path, timestamp=False):
        if not self.dry_run:

            name = os.path.basename(path)
            new_name = name

            if timestamp:
                new_name = '_'.join([datetime.datetime.now().strftime('%Y%m%d_%H%M'), name])

            # make sure all paths exist

            if not os.path.exists(self.DONE_DIR):
                raise CommandError("Tried to archive file, but DONE directory doesn't exist: {0}".format(os.path.abspath(self.DONE_DIR)))

            old_path = os.path.join(self.IN_DIR, name)
            if not os.path.exists(old_path):
                raise CommandError("The old file path doesn't exist: {0}".format(old_path))

            # save this as a courtesy for tests, since they need to move the archived (timestampped) file back
            self.archived_file_path = os.path.join(self.DONE_DIR, new_name)

            os.rename(os.path.join(self.IN_DIR, name), self.archived_file_path)


    def die_if_already_running(self):
        """
            Make sure this script is not already running in another process.
        """
        if os.path.exists(self.pid_file_path):
            raise CommandError("This script is already running in a separate process. (Check {0})".format(self.pid_file_path))


    def set_pid_file(self):
        fh = open(self.pid_file_path, 'w')
        fh.write(str(os.getpid()))
        fh.close()


    def destroy_pid_file(self):
        os.remove(self.pid_file_path)


    def file_has_not_been_written_to_for_over_a_minute(self, file_path):
        """
            Make sure the file has downloaded completely
        """
        now_epoch = time.time()
        last_modified_epoch = os.path.getmtime(file_path)
        return now_epoch - last_modified_epoch > 60

