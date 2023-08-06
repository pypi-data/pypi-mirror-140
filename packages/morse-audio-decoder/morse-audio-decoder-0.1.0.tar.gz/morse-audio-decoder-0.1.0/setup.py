# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['morse_audio_decoder']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22.2,<2.0.0', 'scikit-learn>=1.0.2,<2.0.0']

entry_points = \
{'console_scripts': ['morse-audio-decoder = morse_audio_decoder.__main__:main']}

setup_kwargs = {
    'name': 'morse-audio-decoder',
    'version': '0.1.0',
    'description': 'Decode morse code from input audio file',
    'long_description': None,
    'author': 'Mikko Kouhia',
    'author_email': 'mikko.kouhia@iki.fi',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
