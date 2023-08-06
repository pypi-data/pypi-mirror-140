# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyplexity', 'pyplexity.dataset_processor']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.0.2,<3.0.0',
 'cached-path>=1.0.2,<2.0.0',
 'html5lib>=1.1,<2.0',
 'lxml>=4.7.1,<5.0.0',
 'memory-tempfile>=2.2.3,<3.0.0',
 'nltk>=3.6.7,<4.0.0',
 'pandas>=1.1.5,<2.0.0',
 'storable>=1.2.4,<2.0.0',
 'typer[all]>=0.4.0,<0.5.0',
 'warcio>=1.7.4,<2.0.0']

entry_points = \
{'console_scripts': ['pyplexity = pyplexity.__main__:app']}

setup_kwargs = {
    'name': 'pyplexity',
    'version': '0.1.33',
    'description': 'Perplexity filter for documents and bulc HTML and WARC boilerplate removal.',
    'long_description': '# Pyplexity\n\nThis package provides a simple interface to apply perplexity filters to any document. \nFurthermore, it provides a WARC and HTML bulk processor, with distributed capabilities.\n\n## Usage example\n\nProcess a folder containing a dataset using a trigrams model.\n```\npoetry build\npip3 install dist/pyplexity-0.1.31-py3-none-any.whl\npyplexity bulk-perplexity --perpl-model ../../clueweb-b13-rawtext2/trigrams_bnc.st --perpl-limit 8000.0 \\ \n    --trigrams --base-dir ./cleaned_webkb --output-dir ./perpl_filtered_webkb\n```',
    'author': 'Manuel de Prada Corral',
    'author_email': 'manuel.deprada.corral@usc.es',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
