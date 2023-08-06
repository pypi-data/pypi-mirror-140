# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hitcount',
 'hitcount.conf',
 'hitcount.management',
 'hitcount.management.commands',
 'hitcount.managers',
 'hitcount.migrations',
 'hitcount.models',
 'hitcount.templatetags']

package_data = \
{'': ['*'], 'hitcount': ['locale/ru/LC_MESSAGES/*', 'static/hitcount/*']}

install_requires = \
['Django>=2.2']

setup_kwargs = {
    'name': 'dj-hitcount',
    'version': '1.3.0',
    'description': 'Hit counting application for django',
    'long_description': 'dj-hitcount\n===============\n\n.. image:: https://github.com/abhiabhi94/dj-hitcount/actions/workflows/test.yml/badge.svg?branch=main\n    :target: https://github.com/abhiabhi94/dj-hitcount/actions\n    :alt: Test\n\n.. image:: https://codecov.io/gh/abhiabhi94/dj-hitcount/branch/main/graph/badge.svg?token=JBorE9i0De\n  :target: https://codecov.io/gh/abhiabhi94/dj-hitcount\n  :alt: Coverage\n\n.. image:: https://badge.fury.io/py/dj-hitcount.svg\n    :target: https://pypi.org/project/dj-hitcount/\n    :alt: Latest PyPi version\n\n.. image:: https://img.shields.io/pypi/pyversions/dj-hitcount.svg\n    :target: https://pypi.python.org/pypi/dj-hitcount/\n    :alt: python\n\n.. image:: https://img.shields.io/pypi/djversions/dj-hitcount.svg\n    :target: https://pypi.python.org/pypi/dj-hitcount/\n    :alt: django\n\n.. image:: https://readthedocs.org/projects/dj-hitcount/badge/?version=latest\n    :target: https://dj-hitcount.readthedocs.io/?badge=latest\n    :alt: docs\n\n.. image:: https://img.shields.io/github/license/abhiabhi94/dj-hitcount?color=gr\n    :target: https://github.com/abhiabhi94/dj-hitcount/blob/main/LICENSE\n    :alt: licence\n\n\nBasic app that allows you to track the number of hits/views for a particular object.\n\nThis project was built upon the efforts of `django-hitcount`_. It was made a separate project as the `original one had been stalled`_ for a long time.\n\n.. _`django-hitcount`: https://github.com/thornomad/django-hitcount\n.. _`original one had been stalled`: https://github.com/thornomad/django-hitcount/issues/110\n\n\nDocumentation:\n--------------\n\n`<http://dj-hitcount.rtfd.org>`_\n\nSource Code:\n------------\n\n`<https://github.com/abhiabhi94/dj-hitcount>`_\n\nIssues\n------\n\nUse the GitHub `issue tracker`_ for dj-hitcount to submit bugs, issues, and feature requests.\n\nChangelog\n---------\n\n`<http://dj-hitcount.readthedocs.org/en/latest/changelog.html>`_\n\n.. _issue tracker: https://github.com/abhiabhi94/dj-hitcount/issues\n',
    'author': 'Abhyudai',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/abhiabhi94/dj-hitcount',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
