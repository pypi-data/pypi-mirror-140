# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['pymtheg']
install_requires = \
['spotdl>=3.9.3,<4.0.0']

entry_points = \
{'console_scripts': ['pymtheg = pymtheg:main']}

setup_kwargs = {
    'name': 'pymtheg',
    'version': '1.0.1',
    'description': 'A Python script to share songs from Spotify/YouTube as a 15 second clip.',
    'long_description': "# pymtheg\n\nA Python script to share songs from Spotify/YouTube as a 15 second clip. Designed for\nuse with Termux.\n\n- [Installation](#installation)\n- [Usage](#usage)\n- [Contributing](#contributing)\n- [License](#license)\n\n## Installation\n\npymtheg requires Python 3.6.2 or later.\n\n### From pip\n\n```text\npip install pymtheg\n```\n\n### From main\n\n```text\ngit clone https://github.com/markjoshwel/pymtheg.git\n``````\n\nYou can then either use pip to install the dependencies from requirements.txt, or use Poetry instead.\n\n### Additional Setup for Termux\n\nWrite the following into `$HOME/bin/termux-url-opener`.\n\n```text\n#!/bin/bash\n\npymtheg $1 -d ~/storage/movies/pymtheg/\n```\n\nAlternatively, you can run the following command to obtain the script:\n\n```text\ncurl https://raw.githubusercontent.com/markjoshwel/pymtheg/main/termux-url-opener -o $HOME/bin/termux-url-opener\n```\n\n**Notes:**\n\n- This assumes you have no `$HOME/bin/termux-url-opener` script. If you do, you may have\n to tailer the following instructions to work with your current setup.\n\n- This also assumes that you already have a folder named `pymtheg` in the `Movies`\n  folder of your internal storage, and that you have already ran `termux-setup-storage`\n  to allow access of your internal storage from within Termux. If not, simply adjust the\n  script shown above accordingly.\n\n- If you did not install pymtheg through pip, change `pymtheg` to the path leading to\n  `pymtheg.py`, such as `~/scripts/pymtheg.py`.\n\n- If you have a copy of the repo and use Poetry, change `pymtheg` to\n  `poetry run pymtheg`. However do add a line before the pymtheg invocation to change\n  directories to the repository root or else the `poetry run` invocation will fail.\n\n- Dont forget to `chmod +x` the script after writing!\n\n## Usage\n\n```text\nusage: pymtheg [-h] [-d DIR] [-o OUT] [-sda SDARGS] [-cl CLIP_LENGTH] query\n\na python script to share songs from Spotify/YouTube as a 15 second clip\n\npositional arguments:\n  query                 song/link from spotify/youtube\n\noptions:\n  -h, --help            show this help message and exit\n  -d DIR, --dir DIR     directory to output to\n  -o OUT, --out OUT     output file path, overrides directory arg\n  -sda SDARGS, --sdargs SDARGS\n                        args to pass to spotdl\n  -cl CLIP_LENGTH, --clip-length CLIP_LENGTH\n                        length of output clip in seconds (default 15)\n```\n\nAs pymtheg is built around [spotDL](https://github.com/spotDL/spotify-downloader), you\ncan pass spotDL args to pymtheg. See their documentation for more information!\n\n### Return Codes\n\n- `0`: Successfull\n- `1`: Invalid args\n- `2`: Error during song retrieval\n- `3`: Error during video creation\n\n## Contributing\n\nWhen contributing your first changes, please include an empty commit for copyright waiver\nusing the following message (replace 'John Doe' with your name or nickname):\n\n```text\nJohn Doe Copyright Waiver\n\nI dedicate any and all copyright interest in this software to the\npublic domain.  I make this dedication for the benefit of the public at\nlarge and to the detriment of my heirs and successors.  I intend this\ndedication to be an overt act of relinquishment in perpetuity of all\npresent and future rights to this software under copyright law.\n```\n\nThe command to create an empty commit from the command-line is:\n\n```shell\ngit commit --allow-empty\n```\n\n## License\n\npymtheg is unlicensed with The Unlicense. In short, do whatever. You can find copies of\nthe license in the [UNLICENSE](UNLICENSE) file or in the\n[pymtheg module docstring](pymtheg.py).\n",
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/markjoshwel/pymtheg',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
