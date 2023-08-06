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
    'version': '0.1.1',
    'description': 'Decode morse code from input audio file',
    'long_description': '# Morse audio decoder\n\nThis program is in solution to [Wunderdog Wundernut vol. 11][wundernut], whose instructions can be found in [their GitHub][wundernut-11-github].\n\nThe program reads wav audio file, and outputs decoded morse code in standard output.\n\n## Quickstart\n\n### Installation\n\n#### Option 1 - pip\n\nYou can install this package from pip, with\n\n    pip install morse-audio-decoder\n\n#### Option 2 - Local install from sources\n\nClone code repository from your local machine, install from there:\n\n    git clone https://github.com/mkouhia/morse-audio-decoder.git\n    cd morse-audio-decoder\n    poetry build\n    # take note of the build step output, install package from the dist folder\n    pip install dist/PRODUCED_PACKAGE.whl\n\n### Usage\n\nTo run the script installed with pip, perform\n\n    morse-audio-decoder WAVFILE\n\nor alternatively,\n\n    python -m morse_audio_decoder WAVFILE\n\nwhere `WAVFILE` is path to the audio file to be processed.\n\nThe program decodes audio morse code in the WAVFILE argument, and writes translation to standard output.\nSee program help with command line flag `-h`:\n\n    $ morse-audio-decoder -h\n    usage: morse-audio-decoder [-h] WAVFILE\n\n    Read audio file in WAV format, extract the morse code and write translated text into standard output.\n\n    positional arguments:\n    WAVFILE     Input audio file\n\n    options:\n    -h, --help  show this help message and exit\n\n### Usage in Python\n\n```python\nfrom morse_audio_decoder.morse import MorseCode\n\nmorse_code = MorseCode.from_wavfile("/path/to/file.wav")\nout = morse_code.decode()\nprint(out)\n```\n\n\n## Technical description\n\nThe program works in following steps\n\n1. Read in the WAV file.\n2. Extract [analytic envelope][envelope-wikipedia] from the signal by calculating moving RMS amplitude with [Hann window][hann-wikipedia] of default 0.01 second width. This envelope signal is smooth and always greater than or equal to zero.\n3. Convert envelope to binary 0/1 signal by applying threshold, by default `0.5 * max(envelope)`\n4. Calculate durations of continuous on/off samples\n5. Identify dash/dot characters and different breaks with [K-Means clustering][kmeans-wikipedia]. The lengths of periods are compared, and then labeled automatically based on number of samples.\n6. Create dash/dot character array, which is then broken to pieces by character and word space indices\n7. Translate morse coded characters into plain text, print output\n\nExploratory data analysis and first program implementation is performed in [this jupyter notebook][initial-notebook]. The notebook is not updated; actual implementation differs.\n\n\n### Restrictions\n\nThis decoder has been tested and developed with inputs that have\n- no noise\n- constant keying speed\n- constant tone pitch\n- single input channel.\n\nIf the decoder were to be extended to noisy inputs with major differences, at least following changes would be required\n- pitch detection in moving time\n- signal extraction with narrow bandpass filter, based on identified pitch\n- keying speed detection (characters/words per minute)\n- decoding in smaller time steps, taking into account speed changes.\n\nThe program is also not intended to identify single characters, as the precision will be lower with shorter inputs.\n\n## Development\n\n### Environment\n\nRequirements:\n- Python 3.10\n- Poetry (see [installation instructions][poetry-install])\n\nDependencies:\n- Numpy\n- Scikit-learn\n\n1. Install dependencies with `poetry install`\n2. Enter environment with `poetry shell`\n\n\n### Code quality and testing\n\nAll code is to be formatted with `black`:\n\n    black **/*.py\n\nand code quality checked with `pylint`:\n\n    pylint **/*.py\n\nTests should be written in `pytest`, targeting maximum practical code coverage. Tests are run with:\n\n    pytest\n\nand test coverage checked with\n\n    pytest --cov\n\nOptionally, html test coverage reports can be produced with\n\n    pytest --cov morse_audio_decoder --cov-report html\n\n### Contributions\n\nContributions are welcome. Please place an issue or a pull request.\n\n\n[wundernut]: https://www.wunderdog.fi/wundernut\n[wundernut-11-github]: https://github.com/wunderdogsw/wundernut-vol11\n[envelope-wikipedia]: https://en.wikipedia.org/wiki/Envelope_(waves)\n[hann-wikipedia]: https://en.wikipedia.org/wiki/Hann_function\n[initial-notebook]: notebooks/2022-02-23%20Wundernut%2011%20exploration.ipynb\n[kmeans-wikipedia]: https://en.wikipedia.org/wiki/K-means_clustering\n[poetry-install]: https://python-poetry.org/docs/#installation\n',
    'author': 'Mikko Kouhia',
    'author_email': 'mikko.kouhia@iki.fi',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mkouhia/morse-audio-decoder',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
