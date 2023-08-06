"""
Common tools
"""
import time

from google.cloud import error_reporting

report = error_reporting.Client()


def report_exception(func):
    """Decorator for exceptions. Send error in Google Error Reporting and cancel exception."""

    def exception_wrapper(**kwargs):
        try:
            result = func(**kwargs)
            return result
        except Exception as exc:
            report.report(str(exc)[:2048])

    return exception_wrapper


def timeit(method):
    def wrapper(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result

    return wrapper
