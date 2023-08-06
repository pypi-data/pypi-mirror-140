"""This module estimates the effect measure Non-overlap of All Pairs (NAP),
to be used as a non-Bayesian measure of
difference between EMA Attribute Ratings.

This module is now part of package EmaCalc, but might also be distributed separately.

The NAP measure is a non-parametric estimate of the probability that
Attribute Rating X > Y, given observed ordinal i.i.d. rating samples
x_n drawn from random variable X, and y_n drawn from Y,
X and Y represent two separate Scenarios.
The NAP measure is closely related to the Mann-Whitney statistic for ordinal data.

This module calculates point estimates and approximate confidence intervals for the NAP measure.

There are many ways to estimate a confidence interval for NAP.
Feng et al (2017) studied 29 different methods.
This module uses the "MW-N" variant, defined on page 2607 in their paper,
which showed good performance.
This variant was originally proposed by Newcombe (2009).

*** References:
R. I. Parker and K. Vannest.
An improved effect size for single-case research: Nonoverlap of all pairs.
Behavior Therapy, 40(4):357–367, 2009. doi: 10.1016/j.beth.2008.10.006

D. Feng, G. Cortese, and R. Baumgartner.
A comparison of confidence/credible interval methods for the area under the ROC curve
for continuous diagnostic tests with small sample size.
Statistical Methods in Medical Research, 26(6):2603–2621, 2017.
doi: 10.1177/0962280215602040

R. G. Newcombe.
Confidence intervals for an effect size measure based on the Mann–Whitney statistic.
Part 2: Asymptotic methods and evaluation.
Statistics in Medicine, 25:559–573, 2006. doi: 10.1002/sim.2324

*** Main module function:
nap_statistic --- calculates point estimate and confidence intervals
    for given Attribute-Rating Count arrays

*** Version history:
* Version 0.7:
2021-12-16, first functional version incl. confidence interval
2022-01-03, minor fix to give clearer warning message in case of nan result
"""
import warnings

import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq
import logging

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)  # *** TEST
# ham.logger.setLevel(logging.DEBUG)  # *** TEST


# -----------------------------------------------------------------
def nap_statistic(x, y, p=0.95):
    """Calculate proportion of Non-overlapping Pairs = NAP result,
    = estimate of P(X > Y), given observed ordinal i.i.d. rating samples
    x_n drawn from random variable X, and y_n drawn from Y,
    where X and Y represent two separate Scenarios.
    :param x: array of outcome COUNTS for samples of ordinal random variable X
        x[i, ...] = number of observed samples of i-th ordinal grade
    :param y: array of COUNTS for ordinal random variable Y, similar
        y.shape == x.shape
    :param p: (optional) scalar confidence level
    :return: nap = array with
        nap[0, ...] = lower confidence-interval limit
        nap[1, ...] = point estimate of P(X > Y)
        nap[2, ...] = upper confidence-interval limit
        nap.shape[1:] == x.shape == y.shape
    """
    result_shape = x.shape[1:]
    cum_y = np.cumsum(y, axis=0)
    # cum_y[i] = n Y <= i
    n_y = cum_y[-1]
    n_x = np.sum(x, axis=0)
    n_x_gt_y = np.sum(x[1:, ...] * cum_y[:-1, ...], axis=0)
    # = sum_i number of pairs where X == i AND Y < i
    n_x_eq_y = np.sum(x * y, axis=0)
    # = n pairs where X == Y
    n_pairs = n_x * n_y
    if np.any(n_pairs == 0):
        logger.warning('NO rating pairs -> undefined NAP value in some case(s).')
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')  # suppress standard warning for div by zero
        nap_point = (n_x_gt_y + 0.5 * n_x_eq_y) / n_pairs
    z_p = - norm.ppf((1. - p) / 2)
    ci_low = np.array([nap_ci_low(p, nx, ny, z_p)
                       for (p, nx, ny) in zip(nap_point.reshape((-1,)),
                                              n_x.reshape((-1,)),
                                              n_y.reshape((-1,)))])
    ci_high = np.array([nap_ci_high(p, nx, ny, z_p)
                       for (p, nx, ny) in zip(nap_point.reshape((-1,)),
                                              n_x.reshape((-1,)),
                                              n_y.reshape((-1,)))])
    return np.array([ci_low.reshape(result_shape),
                     nap_point,
                     ci_high.reshape(result_shape)])


def nap_ci_low(a_hat, nx, ny, z_quantile):
    """Calculate lower limit of symmetric confidence interval for NAP
    :param a_hat: scalar point estimate of P(X > Y)
    :param nx: number of X observations
    :param ny: number of Y observations
    :param z_quantile: quantile at higher tail of standard-normal distribution
    :return: scalar ci_low

    Method: MW-N as described by Feng et al (2017),
        using the improved variant solving their nonlinear Eq. (3)
    """
    def fun_3(a):
        """Function to solve Feng et al Eq (3)
        for the LOWER confidence limit, where 0 <= a < a_hat
        :param a: scalar solution candidate
        :return: scalar function value
        """
        return a_hat - a - z_quantile * nap_stdev(a, nx, ny)
    # --------------------------------------------------
    if nx == 0 or ny == 0:
        return np.nan
    if np.isclose(a_hat, 0.):
        return 0.
    ci_lim, res = brentq(fun_3, 0., a_hat, full_output=True)
    if res.converged:
        return ci_lim
    else:
        logger.warning('Confidence-interval calculation did not converge')
        return np.nan


def nap_ci_high(a_hat, nx, ny, z_quantile):
    """Calculate lower limit of symmetric confidence interval for NAP
    :param a_hat: scalar point estimate of P(X > Y)
    :param nx: number of X observations
    :param ny: number of Y observations
    :param z_quantile: quantile at higher tail of standard-normal distribution
    :return: scalar ci_low

    Method: MW-N as described by Feng et al (2017),
        using the improved variant solving their nonlinear Eq. (3)
    """
    def fun_3(a):
        """Function to solve Feng et al Eq (3)
        for the UPPER confidence limit, where a_hat < a <= 1.
        :param a: scalar solution candidate
        :return: scalar function value
        """
        return a - a_hat - z_quantile * nap_stdev(a, nx, ny)
    # --------------------------------------------------
    if nx == 0 or ny == 0:
        return np.nan
    if np.isclose(a_hat, 1.):
        return 1.
    ci_lim, res = brentq(fun_3, a_hat, 1., full_output=True)
    if res.converged:
        return ci_lim
    else:
        logger.warning('Confidence-interval calculation did not converge')
        return np.nan


def nap_stdev(a, nx, ny):
    """Help function to estimate st.dev. of NAP value
    :param a: scalar candidate value for NAP
    :param nx: number of X observations
    :param ny: number of Y observations
    :return: s = sqrt(var(A)), estimated at point NAP A == a

    Method: var_H defined just before Eq (3) in Feng et al (2017)
    """
    n_star = (nx + ny) / 2 - 1
    # = symmetrized as suggested by Newcombe (2009)
    v = a * (1. - a)
    v *= 1. + n_star * ((1. - a) / (2. - a) + a / (1. + a))
    v /= nx * ny
    return np.sqrt(v)


# ------------------------------------------------- TEST:
if __name__ == '__main__':
    print('*** Testing nap_statistic ***')
    x_count = np.array([1, 2, 3, 4, 5])
    y_count = np.array([3, 3, 3, 3, 3])
    print(f'NAP result =\n\t{nap_statistic(x_count, y_count)}')

    print('*** Testing nap_statistic ***')
    x_count = np.array([0, 0, 0, 5])
    y_count = np.array([4, 3, 2, 0])
    print(f'NAP result =\n\t{nap_statistic(x_count, y_count)}')


