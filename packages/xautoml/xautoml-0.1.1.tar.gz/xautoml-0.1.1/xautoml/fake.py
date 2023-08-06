import math
from copy import deepcopy

import numpy as np
from ConfigSpace import ConfigurationSpace, Configuration
from scipy.stats import norm

from xautoml.models import RunHistory


def fake_autosklearn_cpc(rh: RunHistory):
    rh.structures = rh.structures[0:7]

    structure = rh.structures[-1]
    candidate = structure.configs[-1]
    cs: ConfigurationSpace = candidate.config.configuration_space

    key = 'classifier:lda:tol'
    for i in range(20):
        new_candidate = deepcopy(candidate)

        config_dict = new_candidate.config.get_dictionary()
        hp = cs.get_hyperparameter(key)
        config_dict[key] = np.random.uniform(hp.lower, hp.upper)
        new_candidate.config = Configuration(cs, config_dict)

        new_candidate.loss = norm.cdf((config_dict[key] - hp.lower) / (hp.upper - hp.lower))
        new_candidate.runtime['timestamp'] = np.random.random() * new_candidate.runtime['timestamp']
        new_candidate.id = ':'.join([(b, s, c + i) for b, s, c in candidate.id.split(':')])

        structure.configs.append(new_candidate)

    return rh
