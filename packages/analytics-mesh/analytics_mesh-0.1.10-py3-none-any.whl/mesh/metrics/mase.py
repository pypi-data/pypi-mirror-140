import numpy as np
from sklearn.metrics import mean_absolute_error
import logging
log = logging.getLogger(__name__)

def naive_forecasting(actual: np.ndarray, seasonality: int = 1):
    """ Naive forecasting method which just repeats previous samples """
    return actual[:-seasonality]

def mase(actual: np.ndarray, predicted: np.ndarray, seasonality: int = 1):
    """
    It is the mean absolute error of the forecast values, 
    divided by the mean absolute error of the in-sample one-step naive forecast.
    Mean Absolute Scaled Error
    Baseline (benchmark) is computed with naive forecasting (shifted by @seasonality)

   :param actual: An array containing the actual values for a certain period
   :param predicted: An array of predicted values for a certain period
   :param seasonality: The seasonality for the naive forecast (1 means take the previous period/index value as the naive forecast) 
    """
    normal_mae = mean_absolute_error(actual, predicted)
    naive = mean_absolute_error(actual[seasonality:], naive_forecasting(actual, seasonality))
    mase = mean_absolute_error(actual, predicted) / mean_absolute_error(actual[seasonality:], naive_forecasting(actual, seasonality))

    if  mase == np.inf or mase == np.NaN :
        log.info(f"Mase is not an int or a float, value is {mase}")
        log.info(f"The mae of actual vs naive forecast is {naive}")
        log.info(f"The normal mae of actual vs predicted is {normal_mae}")
        log.info("You have likely passed in a dataframe with non-matching indices to perform to naive forecast over, please pass in an array with matching indices")
    return mase

