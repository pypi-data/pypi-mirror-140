"""This module defines a class for individual subject parameter model
to be part of an ema_group.GroupModel instance,
which is part the main Bayesian probabilistic model of EMA data.

Individual parameter distributions are approximated by sampling.
The population mixture model is common prior for all individuals in
the group recruited from the same population.

*** Class Defined here:

IndividualModel: Distribution of individual parameter vector
    assumed to determine the observed EMA data for ONE subject,
    including, in each EMA record,
    (1) a nominal (possibly multi-dimensional) Scenario category, and
    (2) ordinal Ratings for zero, one, or more subjective Attributes.
    The parameter distribution is represented by an array xi with many samples.

*** Version History:
* Version 0.8.1: minor cleanup of comments and logger output

* Version 0.8
2022-02-12, Changed VI factorization for better approximation,
    with individual indicators conditional on parameter samples,
    defining variational q(zeta_n, xi_n) = q(zeta_n | xi_n) q(xi_n)
"""
# *** IndividualModel use BoundedHamiltonianSampler to avoid numerical overflow ? ***
import logging
import warnings

import numpy as np
from scipy.optimize import minimize
from scipy.special import logit, logsumexp, softmax

from samppy import hamiltonian_sampler as ham
from samppy.sample_entropy import entropy_nn_approx as entropy

from EmaCalc.dirichlet_point import JEFFREYS_CONC
# = Jeffreys prior concentration for Dirichlet distribution

from EmaCalc.ema_base import PRIOR_PARAM_SCALE
from EmaCalc.ema_base import response_thresholds, d_response_thresholds
from EmaCalc.ema_base import tau_inv
from EmaCalc.ema_nap import nap_statistic


# -------------------------------------------------------------------
__ModelVersion__ = "2022-02-26"

DITHER_PARAM_SCALE = 0.1 * PRIOR_PARAM_SCALE
# -> initial dithering of point-estimated individual parameters

N_SAMPLES = 1000
# = number of parameter vector samples in each IndividualModel instance

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)  # *** TEST
# ham.logger.setLevel(logging.DEBUG)  # *** TEST sampler


# -------------------------------------------------------------------
class IndividualModel:
    """Container for EMA response data for ONE respondent,
    and a sampled approximation of the individual parameter distribution,
    and corresponding mixture weights for the parameters.

    Individual parameter distributions are approximated by a large set of samples
    stored as property xi, with
    self.xi[s, :] = s-th sample vector of parameters,
    with subsets of parameter types (alpha, beta, eta) as defined by self.base.
    """
    def __init__(self, base, scenario_count, rating_count, xi, rng, prior=None):
        """
        :param base: single common EmaParamBase object, used by all model parts
        :param scenario_count: 2D array with response counts
            scenario_count[k0, k] = number of responses
            in k-th <=> (k1, k2, ...)-th scenario category at k0-th test stage,
            using flattened index for scenario dimensions 1,2,....
            NOTE: ema_data.EmaFrame always stores test stage as first scenario dimension.
        :param rating_count: list of 2D arrays with response counts
            rating_count[i][l, k] = number of responses for i-th ATTRIBUTE,
            at l-th ordinal level, given the k-th <=> (k0, k1, k2, ...)-th scenario
        :param xi: 2D array with parameter sample vector(s)
            xi[s, j] = s-th sample of j-th individual parameter,
                concatenating parameter sub-types as defined in superclass.
        :param rng: random Generator object for sampler
        :param prior: ref to owner GroupModel
        """
        self.base = base
        self.scenario_count = scenario_count
        self.rating_count = rating_count
        self.xi = xi
        self._sampler = ham.HamiltonianSampler(x=self.xi,
                                               fun=self._neg_ll,
                                               jac=self._grad_neg_ll,
                                               epsilon=0.2,
                                               n_leapfrog_steps=10,     # = default
                                               min_accept_rate=0.8,     # = default
                                               max_accept_rate=0.95,    # = default
                                               rng=rng
                                               )
        # keeping sampler properties across learning iterations
        self.prior = prior

    def __repr__(self):
        return (self.__class__.__name__ + '(' +
                '\n\tscenario_count=' + f'{self.scenario_count},' +
                '\n\trating_count=' + f'{self.rating_count},' +
                '\n\txi= array with shape' + f' {self.xi.shape} parameter samples)'
                # f'\n\tw= array with shape' + f' {self.w.shape} weights'
                )

    @classmethod
    def initialize(cls, base, ema_data, rng):  # *** rng -> seed_seq ?
        """Create model from recorded data
        :param base: single common EmaParamBase object
        :param ema_data: list of ema tuples, as stored im ema_data.EmaDataSet instance
        :param rng np.random.Generator for sampler use
        :return: a cls instance
        """
        z = _count_scenarios(ema_data, base.emf)
        # z[t, k] = number of EMA assessments at t-th test stage
        # in k-th <=> (k1, k2, ...)-th scenario, EXCL. k0= test stage
        y = _count_ratings(ema_data, base.emf)
        # y[i][l, k] = number of attribute_grades at l-th ordinal level for i-th ATTRIBUTE question
        # given k-th <=> (k0, k1, k2, ...)-th scenario (INCL. k0= test stage)
        alpha = _initialize_scenario_param(z)
        xi = list(np.ravel(alpha))
        for y_i in y:
            theta = _initialize_rating_theta(y_i).reshape(-1)
            a = base.theta_map.reshape((base.theta_map.shape[0], -1))  # **** needed ?
            beta = np.linalg.lstsq(a.T, theta, rcond=None)[0]
            eta = np.zeros(len(y_i))
            xi.extend(np.concatenate((beta, eta)))
        xi = np.array(xi)
        # dither to N_SAMPLES:
        xi = xi + DITHER_PARAM_SCALE * rng.standard_normal(size=(N_SAMPLES, len(xi)))
        # w = np.ones((len(xi), len(base.comp))) / len(base.comp)  # = None? ****** uniform distribution
        return cls(base, z, y, xi, rng)

    def mean_zeta(self):
        """Expected mean value of mixture-component indicator zeta,
        given self.xi, averaged across all samples in self.xi
        :return: w = 1D array, normalized for sum(w) == 1.
            w[c] = mean P{ self.xi generated by c-th mixture component}
        """
        lr = self.prior.log_responsibility(self.xi)
        w = softmax(lr, axis=0)
        return np.mean(w, axis=1)

    def mean_zeta_xi_mom(self):
        """Moments (0, 1, 2) of xi parameters,
        as defined by current variational q(xi, zeta) = q(zeta | xi) q(xi)
        approximated by average across all samples from q(xi) stored in self.xi,
        to be used for adapting prior mixture-components
        :return: mxi = approx (E[zeta], E[zeta * xi], E[zeta * xi**2]),
            mxi[0] = 1D array = self.mean_zeta() approx E[zeta_c * xi_d],
                    normalized for sum_c mxi[0][c] == 1.
            mxi[1] = 2D array, mxi[1][c, d] approx E[zeta_c * xi_d]
            mxi[2] = 2D array, mxi[2][c, d] approx E[zeta_c * xi_d**2]

        Method: Leijon doc eq:MeanZeta, eq:MeanZetaXi, eq:MeanZetaXi2
        """
        lr = self.prior.log_responsibility(self.xi)
        w = softmax(lr, axis=0)[..., None]
        # w[c, s, 0] = E{zeta_c | self.xi[s, :]}
        # mean_zeta_xi = np.mean(w * self.xi, axis=1)
        # mean_zeta_xi2 = np.mean(w * self.xi**2, axis=1)
        return (np.mean(w, axis=(1, 2)),
                np.mean(w * self.xi, axis=1),
                np.mean(w * self.xi**2, axis=1))

    def _kl_div_zeta(self):
        """KLdiv for indicator variables zeta re prior
        = KLdiv{q(zeta | self.xi) || p(zeta | prior.mix_weight)}
        using current variational q(xi, zeta) = q(zeta | xi) q(xi)
        :return: kl = scalar E{ ln q(zeta | self.xi) - ln p(zeta | prior.mix_weight)}

        Method: Leijon doc eq:VIlowerBoundCalc
        """
        w = softmax(self.prior.log_responsibility(self.xi), axis=0)
        # w[c, s] = E{zeta_c | self.xi[s, :]} Leijon doc eq:ProbZetaGivenXi
        return np.sum(np.mean(w * (np.log(w + np.finfo('float').tiny)  # avoid log(0.) = nan
                                   - self.prior.mix_weight.mean_log[:, None]),
                              axis=1))

    def adapt(self, s_name):
        """Adapt parameter distribution self.xi
        to stored EMA count data, given the current self.w
        and the current estimate of population GMM components self.base.comp.
        :param s_name: subject id, for logger output
        :return: scalar LL = VI lower bound of data log-likelihood, given parameters,
            = E{ ln p(self.scenario_count, self.rating_count | self.xi) }
             - E{ ln q(xi) / prior_p(xi) }_q(xi)
             - KLdiv( q(zeta | xi) || p(zeta || prior.mix_weight)
        Result: Updated self.xi
        """
        # find MAP point first:
        xi_0 = np.mean(self.xi, axis=0)
        res = minimize(fun=self._neg_ll,  # _1,
                       jac=self._grad_neg_ll,  # _1,
                       x0=xi_0)
        if res.success:
            xi_map = res.x.reshape((1, -1))
        else:
            raise RuntimeError(f'{s_name}: MAP search did not converge: '
                               + 'res= ' + repr(res))
        if len(self.xi) != N_SAMPLES:
            # run sampler starting from x_map
            self._sampler.x = xi_map
        else:
            # we have sampled before, start from those samples
            self._sampler.x = self.xi + xi_map - xi_0
        self._sampler.safe_sample(n_samples=N_SAMPLES, min_steps=2)
        self.xi = self._sampler.x
        self.restrict_xi()
        self._sampler.U = self._sampler.potential(self._sampler.x)
        lp_xi = - np.mean(self._sampler.U)
        # lp_xi = E{ ln p(data | xi) + self.prior.logpdf(xi) }_xi
        h_xi = entropy(self.xi)
        # approx = - E{ ln q(xi) }
        kl_zeta = self._kl_div_zeta()
        logger.debug(f'{s_name}: adapt_xi: lp_xi={lp_xi:.3f}. '
                     + f'h_xi= {h_xi:.3f}. '
                     + f'-kl_zeta= {-kl_zeta:.3f}')
        return lp_xi + h_xi - kl_zeta

    def restrict_xi(self):
        """Force mean(theta) -> 0, OR mean(tau) -> 0, after sampling
        for all attributes.
        :return: None
        Result: self.xi = self._sampler.x modified in place
            theta and tau samples modified by same amount
        """
        n_samples = self.xi.shape[0]
        # *** restrict log scenario prob -> normalized prob:
        for sc_slice in self.base.scenario_slices:
            d = logsumexp(self.xi[:, sc_slice], axis=-1, keepdims=True)
            # logger.debug(f'xi scenario restrict d: mean={np.mean(d):.3}; std={np.std(d):.3}; '
            #              + f'max={np.amax(d):.3}; min={np.amin(d):.3}')
            self.xi[:, sc_slice] -= d
        for (a, a_slice) in self.base.attribute_slice_dict.items():
            theta = self.base.attribute_theta(self.xi, a)
            tau = self.base.attribute_tau(self.xi, a)
            if self.base.restrict_attribute:
                d = np.mean(theta.reshape((n_samples, -1)),
                            axis=-1, keepdims=True)
            elif self.base.restrict_threshold:
                d = np.median(tau, axis=-1, keepdims=True)
            else:
                d = 0.
            # d = random offset to be zero-ed out
            n_beta_0 = self.base.beta_0_size()
            # number of beta parameters = first part of a_slice
            beta_slice = slice(a_slice.start,
                               a_slice.start + n_beta_0)
            # = beta slice for FIRST regression effect term
            # logger.debug(f'xi attribute restrict d: mean={np.mean(d):.3}; std={np.std(d):.3}; '
            #              + f'max={np.amax(d):.3}; min{np.amin(d):.3}')
            self.xi[:, beta_slice] -= d
            # adjust tau
            eta = tau_inv(tau - d)
            eta_slice = slice(a_slice.start + self.base.n_beta, a_slice.stop)
            # **** method self.base.eta_slice ???
            self.xi[:, eta_slice] = eta

    def _neg_ll(self, xi):
        """Objective function for self.adapt_xi
        :param xi: 1D or 2D array of candidate parameter vectors
        :return: neg_ll = scalar or 1D array
            neg_ll[...] = - ln P{ self.scenario_count, self.rating_count | xi[..., :]}
                    - ln p(xi[..., :] | self.prior)
            neg_ll.shape == xi.shape[:-1]
        """
        return - self.prior.logpdf(xi) - self.logprob(xi)

    def _grad_neg_ll(self, xi):
        """Gradient of self._neg_ll w.r.t. xi
        :param xi: 1D or 2D array of candidate parameter vectors
        :return: dll = scalar or 1D array
            dll[..., j] = d _neg_ll(xi[..., :]) / d xi[..., j]
            dll.shape == xi.shape
        """
        return - self.prior.d_logpdf(xi) - self.d_logprob(xi)

    def logprob(self, xi):
        """log likelihood of EMA count data, given parameters xi
        :param xi: 1D or 2D array of candidate parameter vectors
        :return: ll = scalar or 1D array
            ll[...] = ln P{ self.scenario_count, self.rating_count | xi[..., :]}
            ll.shape == xi.shape[:-1]
        """
        def scenario_logprob(sc_xi):
            """Log probability mass for scenario categories in ONE test stage
            :param sc_xi: 1D or 2D array with model parameters for ONE test stage
                = alpha = log P{scenarios}, NOT necessarily normalized
            :return: lp = 1D or 2D array with
                lp[..., k] = log P{ k-th scenario | sc_xi[..., :] }
                properly normalized, with sum_k exp(lp[:, k]) == 1.
                lp.shape == sc_xi.shape
            """
            # **** consider using log-Dirichlet here ???
            # NO, this would cause an extra layer in the hierarchy for scenarios,
            # with a log-normal distribution of concentration parameters
            # while these only indirectly determine the probabilities.
            # In the present model, the alpha params directly determine the probabilities.
            return sc_xi - logsumexp(sc_xi, axis=-1, keepdims=True)

        def rating_logprob(a_xi):
            """Log probability mass for rating categories for ONE attribute.
            :param a_xi: 1D or 2D array with model parameters for this attribute
            :return: lp = 2D or 3D array with
                lp[..., l, k] = log P{ l-th ordinal level | k-th scenario, a_xi[..., :] }
            """
            return self.base.rv_class.log_cdf_diff(*self.cdf_args(a_xi))
        # ---------------------------------------------------------------

        ll_z = sum(np.dot(scenario_logprob(xi[..., sc_t]), z_t)
                   for (z_t, sc_t) in zip(self.scenario_count,
                                          self.base.scenario_slices))
        # z_t[k] = k-th scenario count for t-th test stage
        # sc_t = parameter slice for t-th test stage
        ll_y = sum(np.einsum('lk, ...lk -> ...',  # ********* use np.tensordot ???
                             y_i, rating_logprob(xi[..., a_i]))
                   for (y_i, a_i) in zip(self.rating_count,
                                         self.base.attribute_slices))
        # y_i[l, k] = (l, k)-th count for i-th attribute rating
        # a_i = param slice for i-th attribute rating
        return ll_z + ll_y

    def d_logprob(self, xi):
        """Jacobian of self.logprob(xi)
        :param xi: 1D or 2D array with candidate parameter vectors
        :return: d_ll = 2D array
            d_ll[..., j] = d ln P{ self.scenario_count, self.attribute_grades | xi[..., :]} / d xi[..., j]
        """
        def d_scenario_logprob(sc_xi):  # ******** use count input, save RAM ?
            """Gradient of scenario_logprob for ONE test stage
            :param sc_xi: 1D or 2D array with model parameters for ONE test stage
                = alpha = log P{scenarios}, NOT necessarily normalized
            :return: dlp = 2D or 3D array with
                dlp[..., k, j]
                = d log P{ scenario_logprob()[..., k] | sc_xi[..., :] } / d sc_xi[..., j]
            """
            # lp[s, k] = sc_xi[s, k] - ln sum_i(exp(sc_xi[s, i]))
            # dlp[s, k, j] = 1(k==j) - softmax(sc_xi[s, :], axis=-1)[s, j]
            return np.eye(sc_xi.shape[-1]) - softmax(sc_xi[..., None, :], axis=-1)

        # -----------------------------------------------------------------------

        d_ll = [np.einsum('k, ...kj -> ...j',  # ******* use dot or matmul?
                          z_t, d_scenario_logprob(xi[..., sc_t]))
                for (z_t, sc_t) in zip(self.scenario_count,
                                       self.base.scenario_slices)]
        # z_t[k] = k-th count for t-th test stage
        # sc_t = parameter slice for t-th test stage
        for (y_i, a_i) in zip(self.rating_count, self.base.attribute_slices):
            # a_xi = xi[:, a_i]
            a_xi = xi[..., a_i]
            (dlp_low, dlp_high) = self.base.rv_class.d_log_cdf_diff(*self.cdf_args(a_xi))
            # append dlp_d_beta[s, j] = d rating_logprob()[s] / d xi[:, a_i][:, j]
            d_ll.append(np.einsum('...lk, lk, jk -> ...j',
                                  dlp_low + dlp_high, y_i, - self.base.theta_map))  # tensordot 2 steps?
            d_tau_d_eta = d_response_thresholds(a_xi[..., self.base.n_beta:])
            # append dlp_d_eta[..., j] = d rating_logprob()[s] / d xi[:, a_i][:, self.n_beta + j]
            d_ll.append(np.einsum('...lk, lk, ...lj -> ...j',  # *** use dot , matmul ?
                                  dlp_low, y_i, d_tau_d_eta[..., :-1, :]) +
                        np.einsum('...lk, lk, ...lj -> ...j',
                                  dlp_high, y_i, d_tau_d_eta[..., 1:, :]))
            # all d_ll[i][..., :] elements have matching shapes
        return np.concatenate(d_ll, axis=-1)

    def cdf_args(self, a_xi):
        """Extract arguments for rv_class logprob calculation
        :param a_xi: 1D or 2D array with rating-model sample for given attribute a
            a_xi[..., j] = ...-th sample of j-th rating-model parameter
        :return: tuple (arg_low, arg_high) with 2D or 3D array args for probabilistic model,
            such that
            P[ l-th response | ...-th parameter sample, k-th scenario ] =
            = rv_class.cdf(arg_high[..., l, k]) - rv_class.cdf(arg_low[..., l, k])
        """
        theta = np.dot(a_xi[..., :self.base.n_beta], self.base.theta_map)
        # theta[..., k] = ...-th sample of latent variable, given k-th scenario
        # tau_old = self.base.tau(a_xi[..., self.base.n_beta:])
        tau = response_thresholds(a_xi[..., self.base.n_beta:])
        a = tau[..., :-1, None]  # lower interval limits
        b = tau[..., 1:, None]  # upper interval limits
        return a - theta[..., None, :], b - theta[..., None, :]

    def rvs(self, size=N_SAMPLES):
        # re-sample if size != len(self.xi) ???
        return self.xi

    def mean_attribute_grade(self, sc=None):
        """Average raw attribute grades
        :param sc: scenario key, or tuple of scenario keys for result
            grade counts summed across scenario dimensions NOT included in sc
        :return: dict with elements (a, theta), where
            a = attribute key, from self.emf.attribute_grades
            th = mD array with
            th[i0, i1, ...] = mean grade, given scenario
            (self.scenarios[sc[0]][i0], self.scenarios[sc[1]][i1], ...)
            aggregated across other scenario dimensions
        """
        # *** call this only for ONE given attribute at a time, like nap_diff ??? *****
        def mean_grade(a_count, count_axes):
            """Average grade for ONE attribute
            :param a_count: mD array with
                a_count[l, k0, k1, ...] = count of l-th grade, given (k0, k1, ...)-th scenario
            :param count_axes: tuple with a_count axes to keep in result
            :return: g = array with mean grades
                g[i0, i1, ...] = mean grade, given (i0, i1, ...)-th category
                    in self.attribute_rating count_axes, aggregated across other scenario axes
                g.shape == self.base.emf.scenario_shape
            """
            a_count = np.moveaxis(a_count, count_axes,
                                  tuple(range(1, 1 + len(count_axes))))
            sum_axis = tuple(range(1 + len(count_axes), len(a_count.shape)))
            a_count = np.sum(a_count, axis=sum_axis)  # across all other axes
            grades = [1 + i for i in range(a_count.shape[0])]
            g = np.tensordot(grades, a_count,
                             axes=1)
            n_count = np.sum(a_count, axis=0)
            if np.any(n_count == 0):
                logger.warning('NO ratings -> undefined mean in some case(s)')
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')  # suppress standard warning for div by zero
                return g / n_count
        # ----------------------------------------------------------------
        sc_keys = list(self.base.emf.scenarios.keys())
        if sc is None:
            sc = tuple(sc_keys)  # include all scenario dimensions
        if type(sc) is not tuple:
            sc = (sc,)  # must be a tuple
        sc = tuple(sc_i for sc_i in sc if sc_i in sc_keys)
        a_count_axes = tuple(1 + sc_keys.index(sc_i)
                             for sc_i in sc)
        return {a: mean_grade(a_count.reshape((-1, *self.base.emf.scenario_shape)),
                              a_count_axes)
                for (a, a_count) in zip(self.base.emf.attribute_grades.keys(),
                                        self.rating_count)}

    def nap_diff(self, attr_key, sc=None, p=0.95):
        """NAP difference measure for grades of ONE attribute in
            ONE scenario dimension with EXACTLY TWO categories
        :param attr_key: single attribute key for selected result
        :param sc: scenario key, or tuple of scenario keys for result
            grade counts summed across scenario dimensions NOT included in sc
            sc[0] must be scenario dimension with exactly two categories
        :param p: (optional) scalar confidence level
        :return: dict with elements (a, nap), where
            a = attribute key, from self.emf.attribute_grades
            nap = array with
                nap[1, ...] = point estimate(s) and
                nap[[0, 2], ...] = confidence interval, stored as
            nap[:, i1, ...] = NAP difference for scenario dimension sc[0],
                given (i1, ...)-th category in scenario dimension(s) sc[1, ...]
        """
        # *** return a dict for ALL attributes, like mean_attribute_grade ??? *****
        def nap(a_count, count_axes):
            """Non-overlapping Pairs (NAP) difference measure of ONE attribute
            in ONE scenario dimension with exactly two categories
            :param a_count: mD array with
                a_count[l, k0, k1, ...] = count of l-th grade, given (k0, k1, ...)-th scenario
            :param count_axes: tuple with a_count axes to keep in result
            :return: nap = array with mean grades
                nap[i1, ...] = NAP difference, given (i1, ...)-th category
                    in self.attribute_rating count_axes, aggregated across other scenario axes
                g.shape == self.base.emf.scenario_shape
            """
            a_count = np.moveaxis(a_count, count_axes,
                                  tuple(range(1, 1 + len(count_axes))))
            sum_axis = tuple(range(1 + len(count_axes), len(a_count.shape)))
            a_count = np.sum(a_count, axis=sum_axis)  # across all other axes
            nap_u = nap_statistic(a_count[:, 1, ...], a_count[:, 0, ...], p=p)
            # *** calc CI for NAP result ? *********
            return nap_u
        # ----------------------------------------------------------------

        try:
            attr_ind = list(self.base.emf.attribute_grades.keys()).index(attr_key)
            a_count = self.rating_count[attr_ind]
        except ValueError:
            logger.warning(f'Attribute {repr(attr_key)} unknown')
            return None
        sc_keys = list(self.base.emf.scenarios.keys())
        sc_shape = self.base.emf.scenario_shape
        if sc is None:
            try:
                sc = (sc_keys[sc_shape.index(2)],)
            except ValueError:
                sc = (sc_keys[0],)
        if type(sc) is not tuple:
            sc = (sc,)  # must be a tuple, not a single key
        sc = tuple(sc_i for sc_i in sc if sc_i in sc_keys)
        if len(self.base.emf.scenarios[sc[0]]) != 2:
            logger.warning('Can calculate NAP difference only between TWO Scenario categories')
            return dict()
        a_sc_ind = tuple(1 + sc_keys.index(sc_i)
                         for sc_i in sc)
        return nap(a_count.reshape((-1, *sc_shape)),
                   a_sc_ind)


# --------------------------------------------- module help functions:
def _count_scenarios(ema_data, emf):
    """Encode EMA scenario categories as a scenario_count for analysis
    :param ema_data: list of EMA records for ONE respondent
    :param emf: ema_data.EmaFrame instance
    :return: z = 2D array with scenario_counts
        z[t, k] = number of recorded k-th <=> (k1,...)-th scenario category
        at t-th test-stage
        z.shape == (emf.n_stages, emf.n_scenarios / emf.n_stages)
    """
    z = np.zeros(emf.scenario_shape, dtype=int)
    for r in ema_data:
        z[emf.scenario_index(r)] += 1
    return z.reshape((emf.scenario_shape[0], -1))


def _count_ratings(ema_data, emf):
    """Encode EMA ATTRIBUTE attribute_grades as a rating_count list of arrays for analysis
    :param ema_data: list of EMA attribute_grades for ONE respondent
    :param emf: ema_data.EmaFrame instance
    :return: y = list of rating_count arrays,
        y[i][l, k] = number of responses at l-th ordinal level for i-th attribute,
        given the k-th <=> (k0, k1, ...)-th scenario category in the same EMA record
        y[i].shape == (len(emf.attribute_grades[i]), emf.n_scenarios)
    """
    y = [np.zeros((len(r_cat), *emf.scenario_shape), dtype=int)
         for r_cat in emf.attribute_grades.values()]
    for r in ema_data:
        sc_index = emf.scenario_index(r)
        for (i, level_i) in enumerate(emf.rating_index(r)):
            if level_i is not None:  # *** missing attribute_grades are ALLOWED
                y[i][level_i][sc_index] += 1
    for (i, r_cat) in enumerate(emf.attribute_grades.values()):
        y[i] = y[i].reshape((len(r_cat), -1))
    return y


def _initialize_scenario_param(z):
    """Crude initial estimate of scenario logprob parameters
    :param z: array with scenario counts
    :return: alpha = 2D array
        alpha[t, k] = log prob of k-th scenario at t-th test stage
        alpha.shape == (z.shape[0], z[0].size)
    """
    p = z.reshape((z.shape[0], -1)) + JEFFREYS_CONC  # PRIOR_PSEUDO_RESPONDENT
    p /= np.sum(p, axis=-1, keepdims=True)
    return np.log(p)


def _initialize_rating_theta(y):
    """Crude initial estimate of latent sensory variable for ONE attribute question
    :param y: rating_count array,
        y[l, k0, k1, ...] = number of responses at l-th ordinal level,
        given the (k0, k1, ...)-th scenario category
    :return: theta = array of sensory-variable locations
        theta[k0, k1, ...] = estimated location of latent variable,
        given the (k0, k1, ...)-th scenario category
        theta.shape == y[0].shape
    """
    n_levels = y.shape[0]
    expit_th = (np.arange(n_levels) + 0.5) / n_levels
    th = logit(expit_th)
    # back-transformed midpoints in each response interval
    p = y + JEFFREYS_CONC  # PRIOR_PSEUDO_RESPONDENT
    p /= np.sum(p, axis=0, keepdims=True)
    theta = np.tensordot(th, p, axes=1)
    # = typical (midpoint) location, given y
    return theta  # .reshape((theta.shape[0], -1))


# ------------------------------------------------- TEST:
# if __name__ == '__main__':
#     print('*** Testing _nap_statistic ***')
#     x_count = np.array([1, 2, 3, 4, 5])
#     y_count = np.array([0, 1, 2, 3, 4])
#     print(f'NAP result = {nap_statistic(x_count, y_count)}')
#
