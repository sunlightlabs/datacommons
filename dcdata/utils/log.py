import logging
import logging.handlers
import os.path

from settings import LOGGING_EMAIL

def set_up_logger(importer_name, log_path, email_subject):
    # create logger
    log = logging.getLogger(importer_name)
    log.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    ch = logging.FileHandler(os.path.join(log_path, importer_name + '.log'))
    ch.setLevel(logging.DEBUG)

    # create email handler and set level to warn
    eh = logging.handlers.SMTPHandler(
        (LOGGING_EMAIL['host'], LOGGING_EMAIL['port']), # host
        LOGGING_EMAIL['username'], # from address
        ['arowland@sunlightfoundation.com'], # to addresses
        email_subject,
        (LOGGING_EMAIL['username'], LOGGING_EMAIL['password']) # credentials tuple
    )
    eh.setLevel(logging.WARN)

    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    eh.setFormatter(formatter)
    log.addHandler(ch)
    log.addHandler(eh)

    return log

