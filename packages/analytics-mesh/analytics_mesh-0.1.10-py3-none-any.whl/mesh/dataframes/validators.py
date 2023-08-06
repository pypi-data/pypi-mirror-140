from abc import ABCMeta
import pandas as pd
import logging

log = logging.getLogger(__name__)

class Validator(metaclass=ABCMeta):
    pass  # pragma: no cover


class Pandas(Validator):

    # we should deprecate this -22jul2021
    def __init__(self, series: pd.Series):
        self.series = series

    def range(self, min, max):
        """
        validate a series against the range provided
        :param min: the lower bound of an interval
        :param max: the upper bound of an interval
        :return: this validator
        """
        smin = self.series.min()
        smax = self.series.max()
        if smin < min or smax > max:
            raise ValueError('range [{}, {}] not within [{}, {}]'.format(smin, smax, min, max))
        return self


# producing ugliness here but classes  seem unnecessary  - aiming for simplicity
# and operating on a dataframe here directly as a function
def has_duplicates(dataframe, halt=True, row=False):
    """
    determine if a frame has duplicates on the index or row (index by default)
    :param dataframe: a dataframe
    :param halt: raise an exception and stop execution
    :param row: also perform a duplicate row search - this adds to execution time
    """
    res = dict()
    res['index'] = sum(dataframe.index.duplicated())
    if row:
        res['row'] = sum(dataframe.duplicated())

    if sum(res.values()) > 0:
        if halt:
            log.exception(res)
            raise ValueError('duplicates found in frame')
    else:
        return None

    return res

