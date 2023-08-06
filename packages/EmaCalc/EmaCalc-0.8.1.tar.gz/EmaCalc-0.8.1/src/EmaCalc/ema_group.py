"""This module defines classes for a Bayesian probabilistic model of EMA data.

*** Class Overview:

GroupModel: Defines GMM for ONE population,
    and contains all individual response-probability models,
    as implemented by an IndividualModel instance for each subject,
    in ONE group of test subjects, assumed recruited from the SAME population.

ProfileMixtureModel: posterior population model,
    defining a mixture of Student-t distributions for ONE population.

*** Version History:

* Version 0.9 future:
2022-xx-xx, allow multi-processing Pool in GroupModel.adapt, parallel across subjects

* Version 0.8.1
2022-02-26, complete separate GMM for each group, GMM components -> GroupModel property comp
"""
import logging
import copy

import numpy as np
from scipy.special import logsumexp, softmax

from EmaCalc.dirichlet_point import DirichletVector
from EmaCalc.dirichlet_point import JEFFREYS_CONC
# = Jeffreys prior concentration for Dirichlet distribution

from EmaCalc.ema_subject import IndividualModel


# -------------------------------------------------------------------
__ModelVersion__ = "2022-02-28"

PRIOR_MIXTURE_CONC = JEFFREYS_CONC
# = prior conc for sub-population mixture weights.

N_SAMPLES = 1000
# = number of parameter vector samples in each IndividualModel instance

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)  # *** TEST


# -------------------------------------------------------------------
class GroupModel:
    """Container for IndividualModel instances
    for all test subjects in ONE group of respondents,
    and a Gaussian Mixture Model (GMM) representing the parameter distribution in
    the corresponding population of subjects.
    The GMM is implemented by properties
    mix_weight = a MixWeight object with mixture weights in the population,
    comp = a list of gauss_gamma.GaussianRV objects.
    The GMM is prior for the parameter distribution in all IndividualModel objects.
    """
    def __init__(self, base, subjects, mix_weight, comp, rng):
        """
        :param base: single common EmaParamBase object, used by all model parts
        :param subjects: dict with (subject_id, IndividualModel) elements
        :param mix_weight: a single MixtureWeight(DirichletVector) instance,
            with one element for each element of base.comp
        :param comp: list of GaussianRV instances,
            each representing ONE mixture component
            for parameter vector xi, in the (sub-)population represented by self
        :param rng: random Generator instance
        """
        self.base = base
        self.subjects = subjects
        self.mix_weight = mix_weight
        self.comp = comp
        self.rng = rng
        for s in self.subjects.values():
            s.prior = self

    def __repr__(self):
        return (self.__class__.__name__ + '(' +
                f'\n\tsubjects= {len(self.subjects)} individuals,' +
                f'\n\tmix_weight={repr(self.mix_weight)},'
                f'\n\tcomp= {len(self.comp)} mixture components)'
                )

    @classmethod
    def initialize(cls, max_n_comp, base, group_data, seed_seq, rng):
        """Crude initial group model given group EMA data
        :param max_n_comp: integer number of GMM components
        :param base: single common EmaParamBase object, used by all model parts
        :param group_data: a dict with elements (s_id, s_ema), where
            s_id = a subject key,
            s_ema = list with EMA records from an ema_data.EmaDataSet object.
            Each record is a dict with elements (key, category), where
            key can be one of either Scenarios or Ratings keys, and
            category = the recorded response
        :param seed_seq: SeedSequence object to spawn children for subjects of this group
        :param rng: random Generator for this group
        :return: a cls instance crudely initialized
        """
        # v.0.8.1-: including GMM component
        # - v. 0.7.1: use SAME random Generator instance for all subjects
        # s_models = {s_id: IndividualModel.initialize(base, s_ema, rng)
        #             for (s_id, s_ema) in group_data.items()}
        # v. 0.7.2 -: prepare for multi-processing: separate Generator for each subject
        subject_rng_list = [np.random.default_rng(s)
                            for s in seed_seq.spawn(len(group_data))]  # -> gen.expr ?
        s_models = {s_id: IndividualModel.initialize(base, s_ema, s_rng)
                    for ((s_id, s_ema), s_rng) in zip(group_data.items(),
                                                      subject_rng_list)}
        n_subjects = len(s_models)
        if max_n_comp is None:
            max_n_comp = n_subjects // 2
        else:
            max_n_comp = min(n_subjects // 2, max_n_comp)
        mix_weight = MixtureWeight(alpha=np.ones(max_n_comp) * PRIOR_MIXTURE_CONC,
                                   rng=rng)
        comp = [copy.deepcopy(base.comp_prior)
                for _ in range(max_n_comp)]
        return cls(base, s_models, mix_weight, comp, rng)

    def init_comp(self):
        """Initialize Gaussian mixture components to make them distinctly separated,
        using only initialized values for all subject.xi.
        This is a necessary starting point for VI learning.
        :return: None

        Method: pull self.comp elements apart by random method like k-means++
        that tends to maximize separation between components.
        Mixture weights will be adapted later in the general VI procedure.
        """
        def distance(x, c):
            """Square-distance from given samples to ONE mixture component,
            as estimated by component logpdf.
            :param x: 2D array of sample row vectors that might be drawn from c
            :param c: ONE mixture component in self.base.comp
            :return: d = 1D array with non-negative distance measures
                d[n] = distance from x[n] to c >= 0.
                len(d) == x.shape[0]
            """
            d = - c.mean_logpdf(x)
            return d - np.amin(d)

        def weight_by_dist(d):
            """Crude weight vector estimated from given distance measures
            :param d: 1D array with non-negative distances
            :return: w = 1D array with weights,
                with ONE large element randomly chosen with probability prop.to d2,
                and all other elements small and equal.
                w.shape == d.shape
            """
            w = np.full_like(d, 1. / len(d))
            # ALL samples jointly contribute with weight equiv to ONE sample
            i = self.rng.choice(len(d), p=d / sum(d))
            w[i] = len(d) / len(self.comp)
            # total weight of all samples divided uniformly across components
            # placed on the single selected i-th sample point
            return w

        # --------------------------------------------------------
        xi = np.array([np.mean(s_model.xi, axis=0)
                       for s_model in self.subjects.values()])
        xi2 = np.array([np.mean(s_model.xi**2, axis=0)
                        for s_model in self.subjects.values()])
        xi_d = np.full(len(xi), np.finfo(float).max / len(xi) / 2)
        # = very large numbers that can still be normalized to sum == 1.
        for c_i in self.comp:
            c_i.adapt(xi, xi2, w=weight_by_dist(xi_d), prior=self.base.comp_prior)
            xi_d = np.minimum(xi_d, distance(xi, c_i))
            # xi_d[n] = MIN distance from xi[n] to ALL already initialized components

    def adapt(self, g_name):
        """One VI adaptation step for all model parameters
        :param g_name: group id label for logger output
        :return: ll = scalar VI lower bound to data log-likelihood,
            incl. negative contributions for parameter KLdiv re priors

        NOTE: All contributions to VI log-likelihood
        are calculated AFTER all updates of factorized parameter distributions
        because all must use the SAME parameter distribution
        """
        ll_weights = self._adapt_mix_weight()
        # = -KLdiv{ q(self.mix_weight) || prior.mix_weight}
        ll_comp = self._adapt_comp(g_name)
        # ll_comp = list_m -KLdiv(current q(mu_m, Lambda_m) || prior(mu_m, Lambda_m)), for
        # q = new adapted comp, p = prior_comp model, for m-th mixture component
        # Leijon doc eq:CalcLL
        sum_ll_comp = sum(ll_comp)

        # *** future allow multiprocessing across subjects here  *************
        ll_subjects = sum(s_model.adapt(s_name)
                          for (s_name, s_model) in self.subjects.items())
        # = sum <ln p(data | xi)> + <ln prior p(xi | comp)> - <ln q(xi)>
        #           - KLdiv(q(zeta | xi) || p(zeta | v_g)
        #  All ll contributions now calculated using the current updated q() distributions
        logger.debug(f'Group {repr(g_name)}: '
                     + f'\n\tll_weights= {ll_weights:.4f} '
                     + f'\n\tmix_weight.alpha= '
                     + np.array2string(self.mix_weight.alpha,
                                       precision=2,
                                       suppress_small=True)
                     + f'\n\tcomp: -KLdiv= {sum_ll_comp: .3f} = sum'
                     + np.array_str(np.array(ll_comp),
                                    precision=2,
                                    suppress_small=True)
                     + f'\n\tsubject sum ll_xi= {ll_subjects:.3f}')
        return sum_ll_comp + ll_weights + ll_subjects

    def _adapt_comp(self, g_name):
        """One VI update for all GMM components in self.comp
        :param g_name: group id label for logger output
        :return: ll = sum_m (-KLdiv re prior) across self.base.comp[m]
        """
        (m_zeta, m_zeta_xi, m_zeta_xi2) = ([], [], [])
        # = accumulators for <zeta>, <zeta * xi>, <zeta * xi**2>
        # for g in self.groups.values():
        for s in self.subjects.values():
            mxi = s.mean_zeta_xi_mom()
            m_zeta.append(mxi[0])
            m_zeta_xi.append(mxi[1])
            m_zeta_xi2.append(mxi[2])
        ll = [c.adapt(xi_c, xi2_c, w_c, prior=self.base.comp_prior)
              for (c, xi_c, xi2_c, w_c) in zip(self.comp,
                                               np.array(m_zeta_xi).transpose((1, 0, 2)),
                                               np.array(m_zeta_xi2).transpose((1, 0, 2)),
                                               np.array(m_zeta).T)]
        # = list of -KLdiv(comp[c] || comp_prior)
        return ll

    def _adapt_mix_weight(self):
        """One update step of properties self.mix_weight,
        :return: ll = - KLdiv(self.mix_weight || prior.mix_weight), after updated mix_weight
        """
        self.mix_weight.alpha = (np.sum([s.mean_zeta()
                                         for s in self.subjects.values()],
                                        axis=0)
                                 + PRIOR_MIXTURE_CONC)
        # = Leijon doc eq:PosteriorV
        prior_alpha = PRIOR_MIXTURE_CONC * np.ones(len(self.comp))
        return - self.mix_weight.relative_entropy(DirichletVector(alpha=prior_alpha))

    def logpdf(self, xi):
        """Mean log pdf of any candidate subject parameters,
        given current GMM defined by self.mix_weight and self.base.comp
        averaged across self.base.comp parameters and self.mix_weight
        :param xi: array with parameter sample vector(s)
            xi[..., j] = ...-th sample of j-th individual parameter,
        :return: lp = array with
            lp[...] = E_self{ln p(xi[..., :] | self)}
            lp.shape == xi.shape[:-1]

        Method: Leijon doc eq:LogProbXi, prior part
        """
        return logsumexp(self.log_responsibility(xi), axis=0)

    def d_logpdf(self, xi):
        """gradient of self.logpdf(xi) w.r.t. xi
        :param xi: 2D array with parameter sample vector(s)
            xi[..., j] = ...-th sample of j-th individual parameter,
        :return: dlp = array with
            dlp[..., j] = d log p(xi[..., :] | self) / d xi[..., j]
            lp.shape == xi.shape
        """
        return np.sum(softmax(self.log_responsibility(xi)[..., None],
                              axis=0) * self.d_log_responsibility(xi),
                      axis=0)

    def log_responsibility(self, xi):
        """Expected log pdf for any candidate subject parameters,
        for each comp in current GMM represented by self.mix_weight and self.base.comp
        :param xi: 2D array with parameter sample vector(s)
            xi[..., j] = ...-th sample of j-th individual parameter,
        :return: lr = array with
            lr[c, ...] = E{ log P[ xi[..., :] | self.base.comp[c] }
            lr.shape == (len(self.base.comp), xi.shape[:-1])

        Method: Leijon doc l_c(xi) from eq:LogProbXiZeta
        """
        return np.array([c.mean_logpdf(xi) + lv_c
                         for (c, lv_c) in zip(self.comp,
                                              self.mix_weight.mean_log)
                         ])

    def d_log_responsibility(self, xi):
        """Gradient of self.log_responsibility(xi) w.r.t. xi
        :param xi: 2D array with parameter sample vector(s)
            xi[..., j] = ...-th sample of j-th individual parameter,
        :return: dlr = array with
            dlr[c, ..., j] = d self.log_responsibility(xi)[c, ...] / d xi[..., j]
            dlr.shape == (len(self.base.comp), xi.shape)
        """
        return np.array([c.grad_mean_logpdf(xi)
                         for c in self.comp])

    def prune(self, g_name, min_weight=JEFFREYS_CONC):
        """Prune model to keep only active mixture components
        :param g_name: group label for logger output
        :param min_weight: scalar, smallest accepted value for sum individual weight
        :return: None
        Result: all model components pruned consistently
        """
        w_sum = np.sum([s.mean_zeta() for s in self.subjects.values()],
                       axis=0, keepdims=False)
        # = sum of individual mixture weights, given xi
        logger.debug(f'{repr(g_name)}: Before pruning: w_sum = '
                     + np.array2string(w_sum, precision=2, suppress_small=True))
        if np.any(np.logical_and(min_weight < w_sum, w_sum <= 1.5)):
            logger.warning(f'{repr(g_name)}: *** Some component(s) with only ONE member.')
        keep = min_weight < w_sum
        self.mix_weight.alpha = self.mix_weight.alpha[keep]
        del_index = list(np.arange(len(keep), dtype=int)[np.logical_not(keep)])
        del_index.reverse()
        # Must delete in reverse index order to avoid IndexError
        for i in del_index:
            del self.comp[i]
        logger.info(f'{repr(g_name)}: Model pruned to {np.sum(keep)} active mixture component(s) '
                    + f'out of initially {len(keep)}')
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'{repr(g_name)}.subjects.mean_zeta=\n\t'
                         + '\n\t'.join((s_name + ': '
                                        + np.array_str(s_model.mean_zeta(),
                                                       precision=2,
                                                       suppress_small=True)
                                        for (s_name, s_model) in self.subjects.items())))

    def predictive_population_ind(self):
        """Predictive probability-distribution for
        sub-population represented by self
        :return: a ProfileMixtureModel object

        Method: report eq:PredictiveSubPopulation
        """
        comp = [c_m.predictive(rng=self.rng) for c_m in self.comp]
        return ProfileMixtureModel(self.base, comp, self.mix_weight.mean, self.rng)

    def predictive_population_mean(self):
        """Predictive probability-distribution for MEAN parameter vector
        in sub-population represented by self
        :return: a ProfileMixtureModel object

        Method: report eq:PredictiveSubPopulation
        """
        comp = [c_m.mean.predictive(rng=self.rng) for c_m in self.comp]
        return ProfileMixtureModel(self.base, comp, self.mix_weight.mean, self.rng)


# ------------------------------------------------------------------
class ProfileMixtureModel:
    """Help class defining a non-Bayesian predictive model
    for parameter distribution in a population,
    derived from existing trained model components
    """
    def __init__(self, base, comp, w, rng):
        """
        :param base: ref to common EmaParamBase object
        :param comp: list of predictive mixture component models
            NOT same as original base.comp
        :param w: 1D array with mixture weight values
        :param rng: random Generator instance
        """
        self.base = base
        self.comp = comp
        self.w = w
        self.rng = rng

    @property
    def mean(self):
        """Mean of parameter vector, given population mixture,
        averaged across mixture components
        and across posterior distribution of component concentration params.
        :return: 1D array
        """
        return np.dot(self.w, [c_m.mean for c_m in self.comp],
                      axes=1)

    def rvs(self, size=N_SAMPLES):
        """Generate random probability-profile samples from self
        :param size: integer number of sample vectors
        :return: xi = 2D array of parameter-vector samples
            xi[s, :] = s-th sample vector, structured as specified by self.base
        """
        n_comp = len(self.comp)
        # s = RNG.choice(n_comp, p=self.w, size=size)
        s = self.rng.choice(n_comp, p=self.w, size=size)
        # = array of random comp indices
        ns = [np.sum(s == n) for n in range(n_comp)]
        xi = np.concatenate([c.rvs(size=n_m)
                             for (n_m, c) in zip(ns, self.comp)],
                            axis=0)
        self.rng.shuffle(xi, axis=0)
        return xi


# -----------------------------------------------------------------
class MixtureWeight(DirichletVector):
    """Non-Bayesian Dirichlet-distributed weight vector for one mixture distribution
    defined by property
    alpha = 1D concentration vector
    """
    @classmethod
    def initialize(cls, x, rng):  # *** Move to DirichletVector ??? Not needed *******
        """Crude initial setting of concentration parameters
        :param x: array-like 1D list with non-normalized row vector(s)
            that might be generated from a cls instance,
            OR from a multinomial distribution with a cls instance as probability
        :param rng: random.Generator object **** needed ?
        :return: a new cls instance
        """
        # ******* input rng as property if really needed ************
        a = np.array(x) + JEFFREYS_CONC
        # including Jeffreys concentration as pseudo-count
        a /= np.sum(a, axis=-1, keepdims=True)
        a *= JEFFREYS_CONC * a.shape[-1]
        # = normalized with average conc = JEFFREYS_CONC
        return cls(a, rng=rng)   # **** rng ever needed for Ema ???
