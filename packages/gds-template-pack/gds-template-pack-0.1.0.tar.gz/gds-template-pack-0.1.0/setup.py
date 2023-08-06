# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gds_template_pack']

package_data = \
{'': ['*'],
 'gds_template_pack': ['templates/gds/accordion/*',
                       'templates/gds/back-link/*',
                       'templates/gds/breadcrumbs/*',
                       'templates/gds/button/*',
                       'templates/gds/character-count/*',
                       'templates/gds/checkboxes/*',
                       'templates/gds/cookie-banner/*',
                       'templates/gds/date-input/*',
                       'templates/gds/details/*',
                       'templates/gds/error-message/*',
                       'templates/gds/error-summary/*',
                       'templates/gds/fieldset/*',
                       'templates/gds/file-upload/*',
                       'templates/gds/footer/*',
                       'templates/gds/header/*',
                       'templates/gds/inset-text/*',
                       'templates/gds/link/*',
                       'templates/gds/notification-banner/*',
                       'templates/gds/panel/*',
                       'templates/gds/phase-banner/*',
                       'templates/gds/radios/*',
                       'templates/gds/select/*',
                       'templates/gds/skip-link/*',
                       'templates/gds/summary-list/*',
                       'templates/gds/table/*',
                       'templates/gds/tabs/*',
                       'templates/gds/tag/*',
                       'templates/gds/text-input/*',
                       'templates/gds/textarea/*',
                       'templates/gds/warning-text/*']}

setup_kwargs = {
    'name': 'gds-template-pack',
    'version': '0.1.0',
    'description': 'A GOV.UK design system template pack for Django Pattern Library.',
    'long_description': None,
    'author': 'Ben Dickinson',
    'author_email': 'ben.dickinson@torchbox.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
