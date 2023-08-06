
import logging


def __formatter(app_name):
    """
    keeping it pretty dumb so that the caller need not care aobut all the string possiblities
    :return:
    """
    if app_name:
        return f'[{app_name}] %(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s'
    return '%(asctime)s %(levelname)s %(name)s - %(funcName)s: %(message)s'


def get(level=logging.INFO, filename=None, app_name=None, format_override=None):
    """
    A simple logger that will replace a handler on the root logger if called multiple times.
    :param app_name: optional application name
    """
    if not format_override:
        format_override = __formatter(app_name)
    log = logging.getLogger()
    # we nuke the existing handlers whenever this function is called (else they stack)
    log.handlers = []
    formatter = logging.Formatter(format_override)
    log.setLevel(level)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)
    if filename:
        file_handler = logging.FileHandler(filename)
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)
    return log
