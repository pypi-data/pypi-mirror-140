"""This module defines classes and functions to display analysis results
given an EmaModel instance,
learned from a set of data from an EMA study.

Results are shown as figures and tables.
Figures can be saved in various formats, as specified in arguments to display method.
Tables are saved in LaTeX tabular format OR in tab-delimited text files.
Thus, both figures and tables can be easily imported into a LaTeX or word-processing document.

*** Main Class:

EmaDisplaySet = a structured container for all display results

Each display element can be accessed and modified by the user, before saving.

The display set can include data for three types of predictive distributions:
*: a random individual in the (Sub-)Population from which a group of respondents were recruited,
    (most relevant for an experiment aiming to predict the success of a new product,
    among individual potential customers in a population)
*: the mean (=median) in the (Sub-)Population from which a group of test subjects were recruited
    (with interpretation most similar to a conventional significance test)
*: each individual respondent in a Group of test subjects, with observed EMA data


*** Usage Example:
    See main scripts run_ema and run_sim

Figures and tables are automatically assigned descriptive names,
and saved in sub-directories with names constructed from
string labels of Groups and Attributes and Scenarios,
as defined in the ema_data.EmaFrame object of the input ema_model.EmaModel instance.

If there is more than one Group,
    one sub-directory is created for each group,
    and one sub-sub-directory for each requested population / subject predictive result,
    and one sub-sub-sub-directory for each attribute, with results within the group.

Thus, after saving, the display files are stored in a directory structure as, e.g.,
result_path / group / 'population_individual' / attributes / ....
result_path / group / 'population_individual' / scenarios / ....
result_path / group / 'subjects' / subject_id / attributes / ....
result_path / group / 'subjects' / subject_id / scenarios / ....
result_path / group / 'subjects_NAP' / ....  (if user requested NAP results)
result_path / 'group_effects' / 'population_mean' / attributes / ...  (if more than one group)

*** Version History:
* Version 0.8:
2022-02-15, minor cleanup of scenario profile tables

* Version 0.7:
2021-12-19, include table(s) of individual subject NAP results
2021-12-17, display aggregated Attribute effects weighted by Scenario probabilities

* Version 0.6:
2021-12-08, minor checks against numerical overflow

* Version 0.5.1
2021-11-27, allow NO Attributes in model, check display requests, minor cleanup

* Version 0.5
2021-11-05, copied from PairedCompCalc, modified for EmaCalc
2021-11-09, first functional version
"""
# ***** clarify fig_comments and table_comments??
# ***** methods display -> create ?? ****
# ***** local superclass for pretty-printed repr() ?
# ********* allow several Attributes in single plot ?

import numpy as np
from pathlib import Path
import logging
from itertools import product
import string

from . import ema_display_format as fmt

from samppy.credibility import cred_diff, cred_group_diff

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)  # *** TEST

# N_SAMPLES = 1000

# ---------------------------- Default display parameters
FMT = {'scenarios': [],     # list of scenario dimensions to display
       'attributes': [],    # list of (attribute, scenario_effect) to display
       'percentiles': [5., 50., 95.],  # allowing 1, 2, 3, or more percentiles
       'credibility_limit': 0.7,  # min probability of jointly credible differences
       'sc_probability': 'Probability',  # label in figs and tables
       'population_individual': True,  # show result for random individual in population
       'population_mean': True,  # show result for population mean
       'subjects': False,   # show results for each respondent
       'nap': [],   # sequence of (Attribute, Scenarios) NAP results to display
       'nap_confidence': 0.95,  # range for symmetric NAP confidence intervals
       # ******* OR define nap_confidence = (2.5, 97.5) OR use 'percentiles' ?
       'scale_unit': '',  # scale unit for attribute plot axis
       }
# = dict with format parameters that may be changed by user
# Other format parameters are handled in module ema_display_format


def set_format_param(**kwargs):
    """Set / modify format parameters for this module, and module ema_display_format
    Called before any displays are generated.
    :param kwargs: dict with any formatting variables
    :return: None
    """
    other_fmt = dict()
    for (k, v) in kwargs.items():
        k = k.lower()
        if k in FMT:
            FMT[k] = v
        else:
            other_fmt[k] = v
    FMT['percentiles'].sort()  # ensure increasing values
    fmt.set_format_param(**other_fmt)  # all remaining user-defined parameters


# -------------------------------- Main Module Function Interface
def display(ema_model, **kwargs):  # *** not needed ? ***
    """Main function to display default set of EMA analysis results.
    :param: ema_model: a single EmaModel object
    :param: kwargs: (optional) any user-defined display format parameters
    :return: single QualityDisplaySet instance with display results
    """
    return EmaDisplaySet.show(ema_model, **kwargs)


# ------------------------------------------------ Elementary Display Class:
class Profile:
    """Container for ONE selected profile display
    for ONE tuple of one or more scenario dimensions,
    OR for ONE (attribute, scenario_effect)
    """
    def __init__(self, plot=None, tab=None, diff=None):
        """
        :param plot: (optional) FigureRef with profile plot
        :param tab: (optional) TableRef with plotted results tabulated.
        :param diff: (optional) TableRef with credible differences between profile elements.
        """
        self.plot = plot
        self.tab = tab
        self.diff = diff

    def __repr__(self):
        return (self.__class__.__name__ + '(' +
                '\n\t'.join(f'{k}= {repr(v)},'
                            for (k, v) in self.__dict__) +
                '\n\t)')

    def save(self, dir_path):
        """
        :param dir_path: path to directory for saving files
        :return: None
        """
        if self.plot is not None:
            self.plot.save(dir_path)
        if self.tab is not None:
            self.tab.save(dir_path)
        if self.diff is not None:
            self.diff.save(dir_path)


# ---------------------------------------------------------- Top Display Class:
class EmaDisplaySet:
    """Root container for all displays
    of selected predictive scenario and attribute results
    from one ema_model.EmaModel instance learned from an ema_data.EmaDataSet instance.

    All display elements can be saved as files in a selected directory three.
    The complete instance can also be serialized and dumped to a single pickle file,
    then re-loaded, edited, and saved, if user needs to modify some display object.
    """
    def __init__(self, groups, group_effects=None):
        """
        :param groups: dict with (group: GroupDisplaySet) elements
            sub-divided among Attributes
        :param group_effects: (optional) single GroupEffectSet instance,
            showing jointly credible differences between groups,
            if there is more than one group
        """
        # *** store group_effects as dict with (a_label: GroupEffectSet object) ???
        self.groups = groups
        self.group_effects = group_effects

    def __repr__(self):  # *** general superclass for repr?
        return (self.__class__.__name__ + '(' +
                '\n\t'.join(f'{k}= {repr(v)},'
                            for (k, v) in self.__dict__.items()) +
                '\n\t)')

    def save(self, dir_top):
        """Save all displays in a directory tree
        :param dir_top: Path or string with top directory for all displays
        :return: None
        """
        dir_top = Path(dir_top)  # just in case
        for (g, g_display) in self.groups.items():
            g = _dir_name(g, sep='/')
            if len(g) == 0 or all(s in string.whitespace for s in g):
                g_display.save(dir_top)
            else:
                g_display.save(dir_top / g)
        if self.group_effects is not None:
            self.group_effects.save(dir_top / 'group_effects')

    @classmethod
    def show(cls, emm,
             scenarios=None,
             attributes=None,
             nap=None,
             **kwargs):
        """Create displays for all results from an EMA study,
        and store all display elements in a single structured object.
        :param emm: single ema_model.EmaModel instance, with
            emm.groups[group] = ema_model.GroupModel instance,
            emm.groups[group][subject_id] = ema_model.IndividualModel instance
        :param scenarios: (optional) list with selected scenario dimensions to be displayed.
            scenarios[i] = a selected key in emm.emf.scenarios, or a tuple of such keys.
        :param attributes: (optional) list with selected attribute displays to be displayed.
            attributes[i] = a tuple (attribute_key, sc_effect), where
                attribute_key is one key in emm.emf.attribute_grades,
                sc_effect is a scenario key in emm.emf.scenarios, or a tuple of such keys.
                A single key will yield the main effect of the named scenario dimension.
                An effect tuple will also show interaction effects between dimensions,
                IFF the model has been trained to estimate such interaction effects.
        :param nap: (optional) list of selected (attribute, scenario) for desired NAP results.
        :param: kwargs: (optional) dict with any other display formatting parameters
            either for ema_display.FMT or ema_display_format.FMT
        :return: a cls instance filled with display objects
        """
        # get default scale_unit from emm, if not in kwargs
        if 'scale_unit' not in kwargs:
            kwargs['scale_unit'] = emm.base.rv_class.unit_label
        if scenarios is None:
            scenarios = [*emm.base.emf.scenarios.keys()]
            # default showing only main effects for each scenario dimension
        scenarios = [(sc,) if isinstance(sc, str) else sc
                     for sc in scenarios]
        # *** check that requested scenarios exist in model:
        missing_sc = [sc_i for sc_i in scenarios
                      if any(sc_ij not in emm.base.emf.scenarios.keys()
                             for sc_ij in sc_i)]
        for sc in missing_sc:
            logger.warning(f'Scenario profile {sc} unknown in the learned model.')
            scenarios.remove(sc)
        if attributes is None:
            attributes = []
        attributes = [(a, sc) if type(sc) is tuple else (a, (sc,))
                      for (a, sc) in attributes]
        # *** check that requested attribute effects exist in model
        missing_attr = [a_sc for a_sc in attributes
                        if a_sc[0] not in emm.base.emf.attribute_grades.keys()]
        for a_sc in missing_attr:
            logger.warning(f'Attribute effect {a_sc} unknown in the learned model.')
            attributes.remove(a_sc)
        if nap is None:
            nap = []
        else:
            nap = [(a, sc) if type(sc) is tuple else (a, (sc,))
                   for (a, sc) in nap]
        set_format_param(scenarios=scenarios,
                         attributes=attributes,
                         nap=nap,
                         **kwargs)
        # display separate results for each group
        groups = {g: GroupDisplaySet.display(emm_g)
                  for (g, emm_g) in emm.groups.items()}

        if len(groups) > 1:  # prepare for group differences
            group_effects = GroupEffectSet.display(emm)
        else:
            group_effects = None
        logger.info(fig_comments())
        logger.info(table_comments())
        return cls(groups, group_effects)


class GroupDisplaySet:
    """Container for all quality displays related to ONE experimental group:
    Predictive results for the population from which the subjects were recruited,
    and descriptive data for each individual subject, if requested by user.
    """
    def __init__(self,
                 population_mean=None,
                 population_individual=None,
                 subjects=None,
                 nap=None):
        """
        :param population_mean: dict with (a_label: AttributeDisplay object), for population mean,
        :param population_individual: dict with (a_label: AttributeDisplay object), for random individual,
        :param subjects: dict with (s_id: EmaDisplay instance) for participants in one group
            with scenario and attribute results.
        :param nap: dict with (nap_key: nap_table) elements,
            each with results for all subjects in this group
        """
        self.population_mean = population_mean
        self.population_individual = population_individual
        self.subjects = subjects
        self.nap = nap

    def __repr__(self):
        return (self.__class__.__name__ + '(' +
                '\n\t'.join(f'{k}= {repr(v)},'
                            for (k, v) in self.__dict__.items()) +
                '\n\t)')

    def save(self, path):
        """Save all stored display objects in their corresponding sub-trees
        """
        if self.population_mean is not None:
            self.population_mean.save(path / 'population_mean')
        if self.population_individual is not None:
            self.population_individual.save(path / 'population_individual')
        if self.subjects is not None:
            for (s, s_disp) in self.subjects.items():
                s_disp.save(path / 'subjects' / str(s))
        if self.nap is not None:
            for (nap_key, nap_table) in self.nap.items():
                nap_table.save(path / 'subjects_NAP')

    @classmethod
    def display(cls, emm_g):
        """Generate all displays for ONE group
        :param emm_g: dict with elements (a_label: pc_result.PairedCompGroupModel)
        :return: cls instance with all displays for this group
        """
        pop_ind = None
        pop_mean = None
        subjects = None  # ***** empty dict in case no subjects shown
        # attr_corr = None
        if FMT['population_individual']:
            pop_ind = EmaDisplay.display(emm_g.predictive_population_ind())
        if FMT['population_mean']:
            pop_mean = EmaDisplay.display(emm_g.predictive_population_mean())
        if FMT['subjects']:
            # logger.debug('Displaying subjects:')
            subjects = {s: EmaDisplay.display(s_model)
                        for (s, s_model) in emm_g.subjects.items()}
        sc = emm_g.base.emf.scenarios
        nap = dict()
        for nap_sel in FMT['nap']:
            if len(sc[nap_sel[1][0]]) == 2:  # required for NAP calculation
                (attr, a_sc) = nap_sel
                nap[nap_sel] = fmt.nap_table({s: s_model.nap_diff(attr, a_sc,
                                                                  p=FMT['nap_confidence'])
                                              for (s, s_model) in emm_g.subjects.items()},
                                             attribute=attr,
                                             sc_diff=a_sc[0],
                                             case_labels={sc_dim: sc[sc_dim]
                                                          for sc_dim in a_sc[1:]},
                                             conf_level=FMT['nap_confidence'])
            else:
                logger.warning(f'Cannot calculate NAP for {nap_sel}')
        return cls(population_mean=pop_mean,
                   population_individual=pop_ind,
                   subjects=subjects,
                   nap=nap)


# ------------------------------------- Secondary-level displays
class EmaDisplay:
    """Container for all scenario and attribute displays for ONE (Sub-)Population
    either random-individual or mean,
    OR for ONE subject.
    """
    def __init__(self, scenarios, attributes):
        """
        :param scenarios: dict with (scenario_tuple, profile), where
            profile is a Profile instance for the selected scenario_tuple
        :param attributes: dict with (attr_effect, profile), where
            profile is an Profile instance for the selected attr_effect
        """
        self.scenarios = scenarios
        self.attributes = attributes

    def save(self, path):
        """Save all stored display objects in specified (sub-)tree
        :param path: path to directory for saving
        :return: None
        """
        if len(self.scenarios) > 0:
            for (d, sc_display) in self.scenarios.items():
                sc_display.save(path / 'scenarios')
        if len(self.attributes) > 0:
            for (d, a_display) in self.attributes.items():
                a_display.save(path / 'attributes')

    @classmethod
    def display(cls, m_xi):
        """
        :param m_xi: probability model for ema_model parameter vector xi
            either for population-individual, population-mean, or individual subject
        :return: a cls instance
        """
        xi = m_xi.rvs()
        scenarios = {sc: ScenarioProfile.display(xi, m_xi, sc)  # *** m_xi -> base
                     for sc in FMT['scenarios']}
        attributes = {a_effect: AttributeProfile.display(xi, m_xi, a_effect)  # *** m_xi -> base
                      for a_effect in FMT['attributes']}
        return cls(scenarios, attributes)


# ----------------------------------------------------------------------
class ScenarioProfile(Profile):
    """Container for all displays of ONE scenario effect
    in ONE (Sub-)Population, OR for ONE respondent.
    NOTE: Scenario profiles are displayed as
    CONDITIONAL probability of categories in ONE scenario dimension,
    GIVEN categories in other dimension(s), if requested.
    """
    @classmethod
    def display(cls, xi, m_xi, sc_keys):
        """Generate a probability-profile display for selected distribution and factor
        :param xi: 2D array of parameter-vector samples drawn from m_xi
        :param m_xi: a population or individual model instance
        :param sc_keys: tuple of one or more key(s) selected from emf.scenarios.keys()
        :return: single cls instance showing CONDITIONAL probabilities
            for sc_keys[0], GIVEN each combination (j1,..., jD) for sc_keys[1], ...
        """
        emf = m_xi.base.emf
        u = m_xi.base.scenario_prob(xi)
        u /= u.shape[1]  # = JOINT prob mass, incl. TestStage: sum(u) == 1
        u = _aggregate_scenario_prob(u, emf, sc_keys)
        # Now with reordered and aggregated joint probabilities
        # for selected subset of scenario dimensions, such that
        # u[s, j0, j1, ...] = s-th sample of joint probability for
        # emf.scenario[sc_keys[0]][j0], emf.scenario[sc_keys[1]][j1], ... etc.
        # u.shape == (u.shape[0], *emf.scenario_shape[emf.scenario_axes(sc_keys)])
        if len(sc_keys) > 1:
            s = np.sum(u, axis=1, keepdims=True)
            too_small = s <= 0
            n_underflow = np.sum(s <= 0.)
            if n_underflow > 0:
                logger.warning(f'Scenario display: {n_underflow} prob. sample(s) == 0, '
                               + f'with {sc_keys}. '
                               + 'Should not happen! Maybe too few EMA records?')
                s = np.maximum(s, np.finfo(float).tiny)
            u /= s
            # u[:, i, ...] = samples for CONDITIONAL probability of i-th category in sc_keys[0],
            # GIVEN ...-th category product of sc_keys[1:]
            u = u.reshape((*u.shape[:2], -1))
            # now linear-indexed in 3D with
            # u[:, :, j] = prob given j-th product of sc_keys[2:], if any given
            # case_labels[2] = all sc_keys[2:] joined  # ****************** !!!!
        q = np.percentile(u, FMT['percentiles'], axis=0)
        perc = fmt.fig_percentiles(q,
                                   y_label=FMT['sc_probability'],
                                   case_labels=_case_labels(emf.scenarios, sc_keys)
                                   )
        # --------------------------------------- percentile table:
        table = fmt.tab_percentiles(q, perc=FMT['percentiles'],
                                    cdf=None,  # **** always > 0, not displayed
                                    y_label=FMT['sc_probability'],
                                    case_labels=_case_labels(emf.scenarios, sc_keys)
                                    )
        # ---------------------------------------- sc_keys differences
        # NOTE: Comparing CONDITIONAL probabilities of categories in FIRST sc_keys dimension,
        # GIVEN categories in other dimensions.
        d = cred_diff(u, diff_axis=1, sample_axis=0, case_axis=2,
                      p_lim=FMT['credibility_limit'])
        diff = fmt.tab_credible_diff(d,
                                     diff_labels=_product_tuples(emf.scenarios, sc_keys[0:1]),
                                     case_labels=_product_tuples(emf.scenarios, sc_keys[1:])
                                     )
        # ---------------------------------------------------------------------
        return cls(perc, table, diff)


class AttributeProfile(Profile):
    """Container for displays of ONE attribute, and scenario_effect(s),
    in ONE (Sub-)Population, OR for ONE respondent.

    NOTE: Latent-variable results are displayed for each Attribute,
    GIVEN Scenario categories in requested Scenario dimensions,
    averaged across all OTHER Scenario dimension,
    weighted by Scenario probabilities in those dimensions.
    """
    # **** allow several attributes in one display ? *****
    @classmethod
    def display(cls, xi, m_xi, a_effect):
        """Create displays for a single attribute and requested scenario effects
        :param xi: 2D array of parameter-vector samples drawn from m_xi
        :param m_xi: a population or individual model instance
        :param a_effect: tuple(attribute_key, sc_keys)
        :return: single cls instance with all displays
        """
        emf = m_xi.base.emf
        u = m_xi.base.scenario_prob(xi)
        u /= u.shape[1]  # = JOINT prob mass, incl. TestStage: sum(u) == 1
        (a, sc) = a_effect
        # a = attribute key, sc_keys = tuple of scenario keys
        # file_name = a + '_vs_' + '*'.join(sc)
        theta = m_xi.base.attribute_theta(xi, a)
        # theta[s, k0, k1,...] = s-th sample of attribute a, given (k0, k1,...)-th scenario
        theta = _aggregate_scenario_theta(theta, u, emf, sc)
        # theta[s, j0, j1,...] = s-th sample of attribute a,
        #   given (scenarios[sc_keys[0]][j0], scenarios[sc_keys[1]][j1], ...)
        tau = np.median(m_xi.base.attribute_tau(xi, a), axis=0)
        # tau[l] = l-th median rating threshold for attribute a
        q = np.percentile(theta, FMT['percentiles'], axis=0)
        perc = fmt.fig_percentiles(q,
                                   y_label=a + ' (' + FMT['scale_unit'] + ')',
                                   case_labels=_case_labels(emf.scenarios, sc),
                                   cat_limits=tau,
                                   file_label=a)
        # --------------------------------------- percentile table:
        table = fmt.tab_percentiles(q, perc=FMT['percentiles'],
                                    cdf=_sample_cdf_0(theta, axis=0),
                                    y_label=a,
                                    case_labels=_case_labels(emf.scenarios, sc),
                                    file_label=a)
        # ---------------------------------------- attr differences
        # NOTE: comparing all scenario-categories, in all requested sc dimensions
        th_1 = theta.reshape((theta.shape[0], -1))
        # all sc_keys dimensions flattened into th_1[:, 1]
        d = cred_diff(th_1, diff_axis=1, sample_axis=0,
                      p_lim=FMT['credibility_limit'])
        diff = fmt.tab_credible_diff(d,
                                     y_label=a,  # for table header
                                     # diff_head=sc,  # not needed
                                     diff_labels=_product_tuples(emf.scenarios, sc),
                                     file_label=a)
        # ---------------------------------------------------------------------
        return cls(perc, table, diff)


# --------------------------------- classes for differences between groups
class GroupEffectSet:
    """Container for displays of differences between populations,
    as represented by subjects in separate groups
    """
    def __init__(self, population_mean=None, population_individual=None):
        """
        :param population_mean: dict with elements (a_label, AttributeGroupEffects instance)
        :param population_individual: dict with elements (a_label, AttributeGroupEffects instance)
            both with results separated by groups
        """
        self.population_mean = population_mean
        self.population_individual = population_individual

    def save(self, path):
        """Save all stored display objects in their corresponding sub-trees
        """
        if self.population_mean is not None:
            self.population_mean.save(path / 'population_mean')
        if self.population_individual is not None:
            self.population_individual.save(path / 'population_individual')

    @classmethod
    def display(cls, emm):
        """Generate all displays for ONE group
        :param emm: ema_model.EmaModel instance with several groups
        :return: cls instance with all displays of differences
            between predictive distributions for
            population random individual, AND/OR
            population mean
        """
        pop_ind = None
        pop_mean = None
        if FMT['population_individual']:
            pop_ind = EmaGroupDiff.display(emm,
                                           {g: emm_g.predictive_population_ind()
                                            for (g, emm_g) in emm.groups.items()})
        if FMT['population_mean']:
            pop_mean = EmaGroupDiff.display(emm,
                                            {g: emm_g.predictive_population_ind()
                                             for (g, emm_g) in emm.groups.items()})
        return cls(population_mean=pop_mean,
                   population_individual=pop_ind)


class EmaGroupDiff:
    """Container for displays of differences between (Sub-)Populations
    represented by separate ema_model.GroupModel instances.
    """
    def __init__(self, scenarios, attributes):
        """
        :param scenarios: dict with (scenario_tuple, diff_profile), where
            profile is a Profile instance for the selected scenario_tuple
        :param attributes: dict with (attr_effect, diff_profile), where
            profile is an Profile instance for the selected attr_effect
        """
        self.scenarios = scenarios
        self.attributes = attributes

    def save(self, path):
        """Save all stored display objects in specified (sub-)tree
        """
        if len(self.scenarios) > 0:
            for (d, sc_display) in self.scenarios.items():
                sc_display.save(path / 'scenarios')
        if len(self.attributes) > 0:
            for (d, a_display) in self.attributes.items():
                a_display.save(path / 'attributes')

    @classmethod
    def display(cls, emm, groups):
        """
        :param emm: ema_model.EmaModel instance with several groups
        :param groups: dict with elements (g_id, g_model), where
            g_id is a tuple of one or more tuple(group_factor, factor_category),
            g_model is a predictive ema_model.ProfileMixtureModel instance
            i.e. NOT emm.groups
        :return: single cls instance
        """
        xi = [g_model.rvs()
              for g_model in groups.values()]
        # xi[g][s, :] = s-th sample of parameter vector for g-th group
        scenarios = {sc: ScenarioDiff.display(xi, emm, sc)
                     for sc in FMT['scenarios']}
        attributes = {a_effect: AttributeDiff.display(xi, emm, a_effect)
                      for a_effect in FMT['attributes']}
        return cls(scenarios, attributes)


class ScenarioDiff(Profile):
    """Container for all displays of group differences in ONE scenario effect
    """
    @classmethod
    def display(cls, xi, emm, sc_keys):
        """Generate a probability-profile display for selected distribution and factor
        :param xi: list of 2D arrays of parameter-vector samples
            len(xi) == len(emm.groups)
        :param emm: ema_model.EmaModel object
        :param sc_keys: tuple of one or more key(s) selected from emf.scenarios.keys()
        :return: single cls instance
        """
        emf = emm.base.emf
        u = [emm.base.scenario_prob(xi_g) for xi_g in xi]
        # u[g][s, k0, k1, ...] = s-th sample of (k0, k1,...)-th scenario prob in g-th population
        for u_g in u:
            u_g /= u_g.shape[1]  # = JOINT prob mass, incl. k0 = TestStage index:
            # sum(u_g) == 1
        u = [_aggregate_scenario_prob(u_g, emf, sc_keys)
             for u_g in u]
        # Now with reordered and aggregated joint probabilities
        # for selected subset of scenario dimensions, such that
        # u[g, s, j0, j1, ...] = s-th sample of joint probability for
        # emf.scenario[sc_keys[0]][j0], emf.scenario[sc_keys[1]][j1], ... etc.
        # file_name = '_'.join(sc_keys)
        if len(sc_keys) > 1:
            u_check = []
            for u_g in u:
                s = np.sum(u_g, axis=1, keepdims=True)
                n_underflow = np.sum(s <= 0.)
                if n_underflow > 0:
                    logger.warning(f'ScenarioDiff display: {n_underflow} prob. sample(s) == 0. '
                                   + 'Should not happen! Maybe too few responses?')
                    s = np.maximum(s, np.finfo(float).tiny)
                u_check.append(u_g / s)
            u = u_check
            # u = [u_g / np.sum(u_g, axis=1, keepdims=True)
            #      for u_g in u]
            # u[g][s, i, ...] = samples for CONDITIONAL probability of i-th category in sc_keys[0],
            # GIVEN ...-th category product of sc_keys[1:]
            u = [u_g.reshape((u_g.shape[0], -1))
                 for u_g in u]
            # now each u_g linear-indexed in 2D with
            # u[g][s, j] = j-th product of sc_keys
        # ---------------------------------------- sc_keys differences
        # NOTE: Comparing CONDITIONAL probabilities of categories in FIRST sc_keys dimension,
        # GIVEN categories in other dimensions.
        d = cred_group_diff(u, sample_axis=0, case_axis=1,
                            p_lim=FMT['credibility_limit'])
        diff = fmt.tab_credible_diff(d,
                                     diff_labels=emm.groups.keys(),
                                     case_labels=_product_tuples(emf.scenarios, sc_keys)
                                     )
        # ---------------------------------------------------------------------
        return cls(diff=diff)


class AttributeDiff(Profile):
    """Container for all displays of group differences in ONE Attribute-by-Scenario effect
    """
    # **** allow several attributes in one display ? ***************
    @classmethod
    def display(cls, xi, emm, a_effect):
        """Create displays for a single attribute and requested scenario effects
        :param xi: list of 2D arrays of parameter-vector samples
            len(xi) == len(emm.groups)
        :param a_effect: tuple (attr_key, sc_keys), where
            sc_keys is a tuple of one or more key(s) selected from emf.scenarios.keys()
        :param emm: ema_model.EmaModel object
        :return: single cls instance
        """
        emf = emm.base.emf
        u = [emm.base.scenario_prob(xi_g) for xi_g in xi]
        # u[g][s, k0, k1, ...] = s-th sample of (k0, k1,...)-th scenario prob in g-th population
        for u_g in u:
            u_g /= u_g.shape[1]  # = JOINT prob mass, incl. k0 = TestStage index:
            # sum(u_g) == 1
        (a, sc) = a_effect
        # a = attribute key, sc_keys = tuple of scenario keys
        # file_name = a + '_vs_' + '*'.join(sc)
        theta = [emm.base.attribute_theta(xi_g, a)
                 for xi_g in xi]
        # theta[g][s, k0, k1,...] = s-th sample of attribute a, given (k0, k1,...)-th scenario
        theta = [_aggregate_scenario_theta(theta_g, u_g, emf, sc)
                 for (theta_g, u_g) in zip(theta, u)]
        # theta[s, j0, j1,...] = s-th sample of attribute a,
        #   given (scenarios[sc_keys[0]][j0], scenarios[sc_keys[1]][j1], ...)
        #   averaged across OTHER scenarios, weighted by scenario-probabilities.
        # ---------------------------------------- attr differences
        # NOTE: comparing all scenario-categories, in all requested sc dimensions
        th_1 = [theta_g.reshape((theta_g.shape[0], -1))
                for theta_g in theta]
        # all sc_keys dimensions flattened into th_1[g][s, :]
        d = cred_group_diff(th_1, sample_axis=0, case_axis=1,
                            p_lim=FMT['credibility_limit'])
        diff = fmt.tab_credible_diff(d,
                                     y_label=a,
                                     file_label=a,
                                     diff_labels=emm.groups.keys(),
                                     case_labels=_product_tuples(emf.scenarios, sc)
                                     )
        # ---------------------------------------------------------------------
        return cls(diff=diff)


# ---------------------------------- Help functions:
def _aggregate_scenario_prob(u, emf, sc):
    """Aggregate probability-mass samples to keep only selected factor axes
    :param u: multi-dim array with probability-mass samples
        u[s, k0, k1,...] = s-th sample of JOINT prob
            for (k0, k1,...)-th scenario, as defined by emf.scenarios.items()
        u.shape == (n_samples, *emf.scenario_shape)
    :param emf: ema_data.EmaFrame instance for model generating u
    :param sc: tuple with selected scenario keys to display
    :return: array uf with aggregated joint probabilities
        uf[s, j0, j1, ...] = s-th sample of joint probability for
        scenario[sc[0]][j0], scenario[sc[1]][j1], ... etc.
        uf.shape == (u.shape[0], *emf.scenario_shape[emf.scenario_axes(sc)])
    """
    axes = tuple(1 + i for i in emf.scenario_axes(sc))
    uf = np.moveaxis(u, axes, tuple(range(1, 1+len(axes))))
    # with desired sc_keys axes first after 0
    sum_axes = tuple(range(1+len(axes), uf.ndim))
    uf = np.sum(uf, axis=sum_axes)
    # summed across all OTHER axes, except those in sc_keys
    return uf


def _aggregate_scenario_theta(th, u, emf, sc):
    """Aggregate attribute location sample arrays to keep only selected factor axes
    :param th: multi-dim array with attribute-location samples
        th[s, k0, k1,...] = s-th sample of latent variable theta
            in (k0, k1,...)-th scenario, as defined by emf.scenarios.items()
        th.shape == (n_samples, *emf.scenario_shape)
    :param u: multi-dim array with corresponding samples of normalized scenario probabilities
        u[s, k0, k1, ...] = s-th sample of normalized probability of (k0, k1,...)-th scenario
        sum_(k0, k1, ...) u[s, k0, k1, ...] == 1, for all s
        u.shape == th.shape
    :param emf: ema_data.EmaFrame instance for model generating u
    :param sc: tuple with selected scenario keys to display
    :return: th_a = array with aggregated attribute locations
        th_a[s, j0, j1, ...] = s-th sample of conditional attribute location,
        GIVEN scenario[sc[0]][j0], scenario[sc[1]][j1], ... etc.
        averaged across all OTHER Scenarios not included in sc.
        th_a.shape == (n_samples, *emf.scenario_shape[emf.scenario_axes(sc)])

    2021-12-17, probability-averaged across non-included Scenarios
    """
    keep_axes = tuple(1 + i for i in emf.scenario_axes(sc))
    w = np.sum(u, axis=keep_axes, keepdims=True)
    # = normalized scenario prob, for every sample
    th = np.moveaxis(th, keep_axes, tuple(range(1, 1 + len(keep_axes))))
    w = np.moveaxis(w, keep_axes, tuple(range(1, 1 + len(keep_axes))))
    # th and w now with desired sc_keys axes first after sample-axis = 0
    aggregate_axes = tuple(range(1+len(keep_axes), th.ndim))
    # = all OTHER axes, except those in sc_keys
    # th_old = np.mean(th, axis=aggregate_axes)
    # # averaged across all aggregate_axes. version <= 0.6
    th = np.sum(th * w, axis=aggregate_axes)
    # = probability-averaged across all aggregate_axes. version >= 0.7
    return th


def _case_labels(label_dict, key_list):
    """Sequence of case tuples
    :param label_dict: a dict with elements (factor_key, label_list)
    :param key_list: sequence of keys to label_dict
    :return: labels = list of tuples, with
        i-th tuple = (keys[i], label_dict[keys[i])
    """
    # **** return dict instead ??? **************
    return [(gf, label_dict[gf]) for gf in key_list]


def _product_labels(label_dict, key_list):
    """Iterator of tuples, each
    a product of one category from each desired factor dimension
    :param label_dict: a dict with elements (factor_key, label_list)
    :param key_list: list of keys to label_dict
    :return: labels = iterator yielding tuples, with
        ...-th tuple = (label_dict[keys[0][i0], ..., label_dict[keys[D][iD])
        where D = len(keys)
        with last index iD varying fastest, i0 slowest, in the product tuples
    """
    return product(*(label_dict[gf] for gf in key_list))


def _product_tuples(label_dict, keys):
    """Iterator of tuples, each
    a product of one category from each desired factor dimension
    :param label_dict: a dict with elements (factor_key, label_list)
    :param keys: list of keys to label_dict
    :return: labels = iterator yielding tuples, with
        ...-th tuple = ((keys[0]: label_dict[key_list[0][i0]),
                        , (...,), (keys[D]: label_dict[key_list[D][iD])}
        where D = len(key_list)
        with last index iD varying fastest, i0 slowest, in the product tuples
    """
    return product(*(product([gf], label_dict[gf]) for gf in keys))


# def _make_subject_table(a_label, a_model):
#     """Tabulate all quality estimates for all subjects in ONE group, for ONE attribute
#     :param a_label: attribute string label
#     :param a_model: pc_result.PairedCompGroupModel instance
#     :return: a TableRef instance with results for all subjects
#     """
#     pcf = a_model.pcf
#     q = [s_model.quality_samples[..., 1:]
#          for s_model in a_model.subjects.values()]
#     # q[s][n, t, :] = n-th sample vector for s-th subject in t-th test condition
#     # skipping first reference object
#     q_perc = np.array([np.percentile(q_s,
#                                      FMT['percentiles'],
#                                      axis=0)
#                        for q_s in q])
#     # q_perc[s, p, t, i] = p-th percentile of i-th object for s-th subject in t-th test condition
#     cdf = np.array([_sample_cdf_0(q_s) for q_s in q])
#     # cdf[s, t, :] = P[q<= 0] for s-th subject in t-th test condition
#     # *** sort subjects by labels alphabetically
#     s_list = [*a_model.subjects.keys()]
#     s_index = np.argsort(s_list)
#     q_perc = q_perc[s_index, ...]
#     cdf = cdf[s_index, ...]
#     s_list.sort()
#
#     q_perc = q_perc.transpose((1, 0, 2, 3))  # **** for current tab_percentiles
#     # q_perc[p, s, t, i] = n-th sample of i-th object for s-th subject in t-th test condition
#     return fmt.tab_percentiles(q_perc,
#                                cdf=cdf,
#                                perc=FMT['percentiles'],
#                                y_label=a_label,
#                                case_labels=[(FMT['subject'], s_list),
#                                             *pcf.test_factors.items(),
#                                             (FMT['object'], pcf.objects_disp[1:])],
#                                case_order=[FMT['subject'],
#                                            FMT['object'],
#                                            *pcf.test_factors.keys()]
#                                )


def _dir_name(g, sep='_'):
    """make sure group name is a possible directory name
    :param g: string or tuple of strings
    :return: string to be used as directory
    """
    if type(g) is tuple:  # several strings
        g = sep.join(_dir_name(g_s, sep='_')
                     for g_s in g)
    return g


def _sample_cdf_0(u, axis=0):
    """
    Probability that U <= 0 calculated from set of samples.
    :param u: array of samples drawn from U
    :param axis: (optional) axis with independent samples
        e.g., mean of U == np.mean(u, axis=axis)
    :return: array p with
        p[...] = P(U[...] <= 0)
        p.shape == u.shape with axis removed
    """
    n = u.shape[axis]
    return (np.sum(u <= 0, axis=axis) + 0.5) / (n + 1)


def fig_comments():
    """Generate figure explanations.
    :return: comment string
    """
    p_min = np.amin(FMT['percentiles'])
    p_max = np.amax(FMT['percentiles'])
    c = f"""Figure Explanations:
    
Figure files with names like
someScenarioName_xxx.pdf, someAttributeName_xxx.pdf or xxx.jpg, or similar,
display user-requested percentiles (markers) and credible intervals (vertical bars) 
The vertical bars show the range between {p_min:.1f}- and {p_max:.1f}- percentiles.

Median ordinal-response thresholds for perceptual Attributes, if requested,
are indicated by thin lines extending horizontally across the graph.

The credible ranges include all uncertainty
caused both by real inter-individual perceptual differences
and by the limited number of responses by each listener.
"""
    return c


def table_comments():
    c = """Table Explanations:

*** Tables of Percentiles:
Files with names like someScenarioName_xxx.tex, someAttributeName_xxx.tex or *.txt
show numerical versions of the information in corresponding percentile plots.
Percentiles, credible ranges, and marginal probabilities for negative and positive values are shown.

*** Tables of Credible Differences:
Files with names like someAttribute-diff_xxx.tex or *.txt 
show a list of Attribute (in Scenario) pairs
which are ALL JOINTLY credibly different
with the tabulated credibility.
The credibility value in each row is the JOINT probability
for the pairs in the same row and all rows above it.
Thus, the joint probability values already account for multiple comparisons,
so no further adjustments are needed.
"""
    if len(FMT['nap']) > 0:
        c += """\n*** NAP Tables:
Table files with names like someAttribute_sc-dim_xxx.tex or *.txt
show estimated NAP effect(s) of a Scenario Dimension "sc_dim" with exactly TWO categories.
NAP values > 0.5 indicate that the SECOND category is rated higher than the FIRST.
"""
        cl = FMT['nap_confidence']
        c += f'{cl:.1%} Confidence Intervals were estimated by the "MW-N" method (Feng et al., 2017).\n'
    return c
