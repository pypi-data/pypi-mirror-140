import math
import warnings
import logging

import scipy.stats as st
from scipy.stats import skewnorm
from scipy.stats import shapiro
import numpy as np


log = logging.getLogger(__name__)


def __bootstrap_percentile_median_ci(input_array: np.array = None, confidence_level: np.float = None, samples=1000):
    '''
    Calculates a confidence interval for a non-symmetrical distribution. Therefore, distributions that are not normally distributed.
    The function returns an estimated lower limt, median and upper limit for an array, based on bootsrap sampling. The upper and lower
    lower limit are derived form the percentiles of the distribution.
    :param input_array: Array of target data to determine confidence interval for
    :param confidence_level: The level of confidence for the confidence interval of the mean
    :param samples: The number of Bootstrap samples
    '''

    alpha = 1 - confidence_level
    boot_medians = []

    for b in range(samples):
        boot_sample = np.random.choice(input_array, replace=True,
                                       size=len(input_array))  # take a random sample each iteration
        b_median = np.median(boot_sample)  # Median for bootstrap sample b
        boot_medians.append(b_median)
        
    boot_medians = np.array(boot_medians)  # transform it into a numpy array for calculation
    output = [np.quantile(boot_medians, alpha/2), boot_medians.mean(), np.quantile(boot_medians, 1 - alpha / 2)]
    return output


def __bootstrap_percentile_ci(input_array: np.array = None, confidence_level: np.float = None, samples=1000):
    '''
    Calculates a confidence interval for a non-symmetrical distribution. Therefore, distributions that are not normally distributed.
    The function returns an estimated lower limt, median and upper limit for an array, based on bootsrap sampling. The upper and lower
    lower limit are derived form the percentiles of the distribution.
    :param input_array: Array of target data to determine confidence interval for
    :param confidence_level: The level of confidence for the confidence interval of the mean
    :param samples: The number of Bootstrap samples
    '''

    alpha = 1 - confidence_level

    boot_medians = []
    boot_lower = []
    boot_upper = []

    for b in range(samples):
        boot_sample = np.random.choice(input_array, replace=True,
                                       size=len(input_array))  # take a random sample each iteration
        b_median = np.median(boot_sample)  # Median for bootstrap sample b
        b_perc_lower = np.quantile(boot_sample, alpha / 2)  # Lower limit for bootstrap sample b
        b_perc_upper = np.quantile(boot_sample, 1 - alpha / 2)  # Upper limit for bootstrap sample b

        boot_medians.append(b_median)
        boot_lower.append(b_perc_lower)
        boot_upper.append(b_perc_upper)

    boot_medians = np.array(boot_medians)  # transform it into a numpy array for calculation
    boot_lower = np.array(boot_lower)
    boot_upper = np.array(boot_upper)

    output = [boot_lower.mean(), boot_medians.mean(), boot_upper.mean()]
    return output


def __normal_big_ci(input_array: np.array = None, confidence_level: np.float = None, standard_error=None):
    """
    Returns a point estimate and a confidence interval for a Large array of observations where distribution is not normal
    :param input_array: Array of target data to determine confidence interval over
    :param confidence_level: The level of confidence for the confidence interval, expressed as a fraction 0.00-1.00.
    :param standard_error: The approximate standard deviation of a statistical sample population.
    """

    ll = input_array.mean() - st.norm.ppf(confidence_level) * standard_error
    ul = input_array.mean() + st.norm.ppf(confidence_level) * standard_error
    output = [ll, input_array.mean(), ul]
    return output


def __normal_small_ci(input_array: np.array = None, confidence_level: np.float = None, standard_error=None):
    """
    Returns a point estimate and a confidence interval for a Small array of observations where distribution is not normal
    :param input_array: Array of target data to determine confidence interval over
    :param confidence_level: The level of confidence for the confidence interval, expressed as a fraction 0.00-1.00.
    :param standard_error: The approximate standard deviation of a statistical sample population.
    """

    ll = input_array.mean() - st.t.ppf(confidence_level, len(input_array) - 1) * standard_error
    ul = input_array.mean() + st.t.ppf(confidence_level, len(input_array) - 1) * standard_error
    output = [ll, input_array.mean(), ul]
    return output


def __normality_check(input_array=None, confidence_level=None):
    """
    Returns a point estimate and a confidence interval for a Small array of observations where distribution is not normal
    :param input_array: Array of target data to determine confidence interval over
    :param confidence_level: The level of confidence for the confidence interval, expressed as a fraction 0.00-1.00.
    """

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        _, p = shapiro(input_array)
        if p > (1 - confidence_level):
            return True
        else:
            return False


def confidence_interval(input_array: np.array = None, confidence_level: np.float = None, conf_int_mean: np.bool = None,
                        unique_key=None, seed=0) -> list:
    """
    Returns a point estimate and a confidence interval for an array of observations

    :param input_array: Array of target data to determine confidence interval over
    :param confidence_level: The level of confidence for the confidence interval, expressed as a fraction 0.00 - 1.00
    :param conf_int_mean: Flag for calculating the confidence interval around the mean, default False, will calculate the confidence interval around the observations
    :param unique_key: The unique key that is being iterated over or what the confidence interval is for
    :param seed: This is the seed value that gets set, this allows the function to be deterministic
    :return: a point estimate and a confidence interval for an array of observations.
    """

    np.random.seed(seed)

    if np.array(input_array).size == 0:
        observation_count = 0
        log.warning(f"The array is empty, cannot compute confidence interval for :{unique_key}")
        output = [np.nan, 0, np.nan]
        return output
    else:
        observation_count = len(input_array)

        if conf_int_mean is True:
            log.info("Calculating the confidence interval around the mean of the observations")
            denominator = math.sqrt(observation_count)

        else:
            denominator = 1

    standard_error = input_array.std() / denominator
    # Check if there is enough data to perform hypothesis test
    if observation_count <= 3:
        log.warning(
            f"{observation_count} observations is not enough to create a confidence interval for unique key {unique_key}")
        output = [np.nan, input_array.mean(), np.nan]
        return output

    if confidence_level == 0.00 or confidence_level == 1.00:
        log.warning(
            f"A confidence level of :{confidence_level} will return -inf and positive inf values, please use values 0.01-0.99")
        output = [-np.inf, input_array.mean(), np.inf]
        return output

    if __normality_check(input_array, confidence_level):  # if distribution is normal
        log.info(f"The distribution for the unique key {unique_key} is normal")

        if observation_count > 30:  # Large sample (n>30)
            return __normal_big_ci(input_array, confidence_level, standard_error)

        else:  # Small sample (n<=30)
            return __normal_small_ci(input_array, confidence_level, standard_error)

    else:
        if conf_int_mean:  # if this is True
            return __bootstrap_percentile_median_ci(input_array, confidence_level, 1000)            

        else:
        # now we check for if the condition is == False
            log.info(f"The distribution for the unique key {unique_key} is not normal")
            return __bootstrap_percentile_ci(input_array, confidence_level, denominator)

