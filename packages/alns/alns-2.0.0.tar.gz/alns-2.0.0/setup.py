# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['alns',
 'alns.criteria',
 'alns.criteria.tests',
 'alns.tests',
 'alns.weight_schemes',
 'alns.weight_schemes.tests']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=2.2.0', 'numpy>=1.15.2']

setup_kwargs = {
    'name': 'alns',
    'version': '2.0.0',
    'description': 'A flexible implementation of the adaptive large neighbourhood search (ALNS) algorithm.',
    'long_description': '[![PyPI version](https://badge.fury.io/py/alns.svg)](https://badge.fury.io/py/alns)\n[![Build Status](https://app.travis-ci.com/N-Wouda/ALNS.svg?branch=master)](https://app.travis-ci.com/N-Wouda/ALNS)\n[![codecov](https://codecov.io/gh/N-Wouda/ALNS/branch/master/graph/badge.svg)](https://codecov.io/gh/N-Wouda/ALNS)\n\nThis package offers a general, well-documented and tested\nimplementation of the adaptive large neighbourhood search (ALNS)\nmeta-heuristic, based on the description given in [Pisinger and Ropke\n(2010)][1]. It may be installed in the usual way as,\n\n```\npip install alns\n```\n\n## How to use\nThe `alns` package exposes two classes, `ALNS` and `State`. The first\nmay be used to run the ALNS algorithm, the second may be subclassed to\nstore a solution state - all it requires is to define an `objective`\nmember function, returning an objective value.\n\nThe ALNS algorithm must be supplied with a _weight scheme_ and an _acceptance\ncriterion_.\n\n### Weight scheme\nThe weight scheme determines how to select destroy and repair operators in each\niteration of the ALNS algorithm. Several have already been implemented for you,\nin `alns.weight_schemes`:\n\n- `SimpleWeights`. This weight scheme applies a convex combination of the \n   existing weight vector, and a reward given for the current candidate \n   solution.\n- `SegmentedWeights`. This weight scheme divides the iteration horizon into\n   segments. In each segment, scores are summed for each operator. At the end\n   of each segment, the weight vector is updated as a convex combination of \n   the existing weight vector, and these summed scores.\n\nEach weight scheme inherits from `WeightScheme`, which may be used to write \nyour own.\n\n### Acceptance criterion\nThe acceptance criterion determines the acceptance of a new solution state at\neach iteration. An overview of common acceptance criteria is given in\n[Santini et al. (2018)][3]. Several have already been implemented for you, in\n`alns.criteria`:\n\n- `HillClimbing`. The simplest acceptance criterion, hill-climbing solely\n  accepts solutions improving the objective value.\n- `RecordToRecordTravel`. This criterion accepts solutions when the improvement\n  meets some updating threshold.\n- `SimulatedAnnealing`. This criterion accepts solutions when the\n  scaled probability is bigger than some random number, using an\n  updating temperature.\n\nEach acceptance criterion inherits from `AcceptanceCriterion`, which may\nbe used to write your own.\n\n### Examples\nThe `examples/` directory features some example notebooks showcasing\nhow the ALNS library may be used. These include:\n\n- The travelling salesman problem (TSP), [here][2]. We solve an\n  instance of 131 cities to within 2.1% of optimality, using simple\n  destroy and repair heuristics with a post-processing step.\n- The cutting-stock problem (CSP), [here][4]. We solve an instance with\n  180 beams over 165 distinct sizes to within 1.35% of optimality in\n  only a very limited number of iterations.\n\nFinally, the weight schemes and acceptance criteria notebook gives an overview\nof various options available in the `alns` package. In the notebook we use these\ndifferent options to solve a toy 0/1-knapsack problem. The notebook is a good\nstarting point for when you want to use the different schemes and criteria \nyourself. It is available [here][5].\n\n## References\n- Pisinger, D., and Ropke, S. (2010). Large Neighborhood Search. In M.\n  Gendreau (Ed.), _Handbook of Metaheuristics_ (2 ed., pp. 399-420).\n  Springer.\n- Santini, A., Ropke, S. & Hvattum, L.M. (2018). A comparison of\n  acceptance criteria for the adaptive large neighbourhood search\n  metaheuristic. *Journal of Heuristics* 24 (5): 783-815.\n\n[1]: http://orbit.dtu.dk/en/publications/large-neighborhood-search(61a1b7ca-4bf7-4355-96ba-03fcdf021f8f).html\n[2]: https://github.com/N-Wouda/ALNS/blob/master/examples/travelling_salesman_problem.ipynb\n[3]: https://link.springer.com/article/10.1007%2Fs10732-018-9377-x\n[4]: https://github.com/N-Wouda/ALNS/blob/master/examples/cutting_stock_problem.ipynb\n[5]: https://github.com/N-Wouda/ALNS/blob/master/examples/weight_schemes_acceptance_criteria.ipynb\n',
    'author': 'Niels Wouda',
    'author_email': 'n.wouda@apium.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/N-Wouda/ALNS',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
