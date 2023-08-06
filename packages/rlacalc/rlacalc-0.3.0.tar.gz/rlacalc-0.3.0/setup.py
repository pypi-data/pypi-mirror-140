# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['rlacalc']

package_data = \
{'': ['*']}

modules = \
['hug_noop']
entry_points = \
{'console_scripts': ['rlacalc = rlacalc:main']}

setup_kwargs = {
    'name': 'rlacalc',
    'version': '0.3.0',
    'description': 'Statistical calculations for risk-limiting election tabulation audits (RLAs)',
    'long_description': '**rlacalc** crunches the numbers for risk-limiting post-election audits.\nIt can calculate sample sizes, as well as calculate risk levels based on observed ballots.\nIt can handle many of the commonly used RLA tests, including ballot-level comparison via Kaplan-Markov and\nballot polling via BRAVO.\n\n# Goals\nIt is important to emphasize that the output of an audit should be\na report providing evidence related to election outcome, details about and explanations of any discrepancies found,\nand conclusions based on that evidence.  See the paper\n[Evidence-Based Elections Stark and Wagner](http://www.stat.berkeley.edu/~stark/Preprints/evidenceVote12.pdf)\nand the report [Risk-Limiting Post-Election Audits: Why and How](http://www.stat.berkeley.edu/~stark/Preprints/RLAwhitepaper12.pdf).\n\nrlacalc helps observers to explore the best way to do an audit beforehand, and to check the numbers in reports published after an audit, e.g. as described for a [Public RLA Oversight Protocol](http://bcn.boulder.co.us/~neal/elections/PublicRLAOversightProtocol.pdf).\n\nrlacalc can be used to perform calculations from the command line or used as a library in Python. In addition, if the hug package\nis available, it can be accessed over the web.\n\n# Installation\n\nrlacalc works with Python 2.7 and Python 3.x.\nThere are no other mandatory dependencies beyond the standard library.\n\nIf hug is installed, rlacalc can be deployed via a web server.\n\n# Usage\n\n```\n$ rlacalc --help\n...\n\n$ rlacalc --test\n...\n\n$ rlacalc -m 1 -n\nSample size = 479 for margin 1%, risk 10%, gamma 1.03905, o1 0, o2 0, u1 0, u2 0\n\n$ rlacalc -m 1 -n --o1 1\nSample size = 615 for margin 1%, risk 10%, gamma 1.03905, o1 1, o2 0, u1 0, u2 0\n\n$ rlacalc -m 3 -r 5\nKM_exp_rnd  = 226 for margin 3%, risk 5%, gamma 1.03905, or1 0.001, or2 0.0001, ur1 0.001, ur2 0.0001, roundUp1 1, roundUp2 0\n```\n\n# Background\nFor tools implemented in javascript, with plots, see\n\n* [Tools for Comparison Risk\\-Limiting Election Audits](https://www.stat.berkeley.edu/~stark/Vote/auditTools.htm)\n* [Tools for Ballot\\-Polling Risk\\-Limiting Election Audits](https://www.stat.berkeley.edu/~stark/Vote/ballotPollTools.htm)\n\n# History\nrlacalc was included as part of [audit_cvrs](https://github.com/nealmcb/audit_cvrs) in 2015 to help run some early pilot audits in Colorado as part of the [The Colorado Risk-Limiting Audit Project (CORLA)](http://bcn.boulder.co.us/~neal/elections/corla/).\n',
    'author': 'Neal McBurnett',
    'author_email': 'neal@mcburnett.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://bcn.boulder.co.us/~neal/electionaudits/rlacalc.html',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
