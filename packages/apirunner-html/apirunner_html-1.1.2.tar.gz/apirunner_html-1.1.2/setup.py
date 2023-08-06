# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['apirunner_html']

package_data = \
{'': ['*'], 'apirunner_html': ['static/css/*', 'static/js/*', 'templates/*']}

install_requires = \
['Flask==1.1.2',
 'Jinja2==2.11.2',
 'MarkupSafe==0.23',
 'ansi2html==1.6.0',
 'pytest_html==2.1.1']

entry_points = \
{'console_scripts': ['apirunner_html = apirunner_html:shell'],
 'pytest11': ['apirunner_html = apirunner_html.report']}

setup_kwargs = {
    'name': 'apirunner-html',
    'version': '1.1.2',
    'description': 'The HTML Report for Python api testing Base on PyTestReport and pytest_html',
    'long_description': None,
    'author': 'ylfeng',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
}


setup(**setup_kwargs)
