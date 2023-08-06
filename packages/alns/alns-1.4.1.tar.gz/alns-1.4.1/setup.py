# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['alns', 'alns.criteria', 'alns.criteria.tests', 'alns.tests', 'alns.tools']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=2.2.0', 'numpy>=1.15.2']

setup_kwargs = {
    'name': 'alns',
    'version': '1.4.1',
    'description': 'A flexible implementation of the adaptive large neighbourhood search (ALNS) algorithm.',
    'long_description': '[![PyPI version](https://badge.fury.io/py/alns.svg)](https://badge.fury.io/py/alns)\n[![Build Status](https://app.travis-ci.com/N-Wouda/ALNS.svg?branch=master)](https://app.travis-ci.com/N-Wouda/ALNS)\n[![codecov](https://codecov.io/gh/N-Wouda/ALNS/branch/master/graph/badge.svg)](https://codecov.io/gh/N-Wouda/ALNS)\n\nThis package offers a general, well-documented and tested\nimplementation of the adaptive large neighbourhood search (ALNS)\nmeta-heuristic, based on the description given in [Pisinger and Ropke\n(2010)][1]. It may be installed in the usual way as,\n\n```\npip install alns\n```\n\n## How to use\nThe `alns` package exposes two classes, `ALNS` and `State`. The first\nmay be used to run the ALNS algorithm, the second may be subclassed to\nstore a solution state - all it requires is to define an `objective`\nmember function, returning an objective value.\n\nThe ALNS algorithm must be supplied with an acceptance criterion, to\ndetermine the acceptance of a new solution state at each iteration.\nAn overview of common acceptance criteria is given in [Santini et al.\n(2018)][3]. Several have already been implemented for you, in\n`alns.criteria`,\n\n- `HillClimbing`. The simplest acceptance criterion, hill-climbing\n  solely accepts solutions improving the objective value.\n- `RecordToRecordTravel`. This criterion only accepts solutions when\n  the improvement meets some updating threshold.\n- `SimulatedAnnealing`. This criterion accepts solutions when the\n  scaled probability is bigger than some random number, using an\n  updating temperature.\n\nEach acceptance criterion inherits from `AcceptanceCriterion`, which may\nbe used to write your own.\n\n### Examples\nThe `examples/` directory features some example notebooks showcasing\nhow the ALNS library may be used. Of particular interest are,\n\n- The travelling salesman problem (TSP), [here][2]. We solve an\n  instance of 131 cities to within 2.1% of optimality, using simple\n  destroy and repair heuristics with a post-processing step.\n- The cutting-stock problem (CSP), [here][4]. We solve an instance with\n  180 beams over 165 distinct sizes to within 1.35% of optimality in\n  only a very limited number of iterations.\n\n## References\n- Pisinger, D., and Ropke, S. (2010). Large Neighborhood Search. In M.\n  Gendreau (Ed.), _Handbook of Metaheuristics_ (2 ed., pp. 399-420).\n  Springer.\n- Santini, A., Ropke, S. & Hvattum, L.M. (2018). A comparison of\n  acceptance criteria for the adaptive large neighbourhood search\n  metaheuristic. *Journal of Heuristics* 24 (5): 783-815.\n\n[1]: http://orbit.dtu.dk/en/publications/large-neighborhood-search(61a1b7ca-4bf7-4355-96ba-03fcdf021f8f).html\n[2]: https://github.com/N-Wouda/ALNS/blob/master/examples/travelling_salesman_problem.ipynb\n[3]: https://link.springer.com/article/10.1007%2Fs10732-018-9377-x\n[4]: https://github.com/N-Wouda/ALNS/blob/master/examples/cutting_stock_problem.ipynb\n',
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
