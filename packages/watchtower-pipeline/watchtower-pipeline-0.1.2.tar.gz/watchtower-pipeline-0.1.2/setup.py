# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['watchtower_pipeline']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0', 'tqdm>=4.62.3,<5.0.0']

entry_points = \
{'console_scripts': ['package-watchtower-vue = scripts:package_watchtower_vue']}

setup_kwargs = {
    'name': 'watchtower-pipeline',
    'version': '0.1.2',
    'description': 'Utilities to generate static data for Watchtower.',
    'long_description': '# Watchtower Pipeline Tools\n\nIn order to generate data for Watchtower, follow these steps:\n\n* `python -m venv .venv`\n* `source .venv/bin/activate`\n* `pip install watchtower-pipeline`\n* Create a `.env.local` file as follows:\n\n```\nKITSU_DATA_SOURCE_URL=https://<your-kitsu-instance>/api\nKITSU_DATA_SOURCE_USER_EMAIL=user@example.org\nKITSU_DATA_SOURCE_USER_PASSWORD=password\n```\n\n* Run `python -m watchtower_pipeline.kitsu -b`\n* Copy the content of the `watchtower` folder into your webserver\n* Alternatively you can navigate to the folder and run `python -m http.server`\n',
    'author': 'Francesco Siddi',
    'author_email': 'francesco@blender.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
