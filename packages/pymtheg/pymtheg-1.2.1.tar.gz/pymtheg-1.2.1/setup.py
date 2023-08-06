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
    'version': '1.2.1',
    'description': 'A Python script to share songs from Spotify/YouTube as a 15 second clip.',
    'long_description': "# pymtheg\n\nA Python script to share songs from Spotify/YouTube as a 15 second clip. Designed for\nuse with Termux.\n\nSee the [repository](https://github.com/markjoshwel/pymtheg) for more installation and\ncontribution instructions/information.\n\n## Usage\n\n```text\nusage: pymtheg [-h] [-d DIR] [-o OUT] [-sda SDARGS] [-ffa FFARGS] [-cl CLIP_LENGTH] [-ud] query\n\na python script to share songs from Spotify/YouTube as a 15 second clip\n\npositional arguments:\n  query                 song/link from spotify/youtube\n\noptions:\n  -h, --help            show this help message and exit\n  -d DIR, --dir DIR     directory to output to\n  -o OUT, --out OUT     output file path, overrides directory arg\n  -sda SDARGS, --sdargs SDARGS\n                        args to pass to spotdl\n  -ffa FFARGS, --ffargs FFARGS\n                        args to pass to ffmpeg for clip creation\n  -cl CLIP_LENGTH, --clip-length CLIP_LENGTH\n                        length of output clip in seconds (default 15)\n  -ud, --use-defaults   use 0 as clip start and --clip-length as clip end\n\nffargs default: '-hide_banner -loglevel error -loop 1 -c:a aac -vcodec libx264 -pix_fmt yuv420p -preset ultrafast -tune\nstillimage -shortest'\n```\n\n## License\n\npymtheg is unlicensed with The Unlicense. In short, do whatever. You can find copies of\nthe license in the\n[UNLICENSE](https://github.com/markjoshwel/pymtheg/blob/main/UNLICENSE) file or in the\n[pymtheg module docstring](https://github.com/markjoshwel/pymtheg/blob/main/pymtheg.py#L5).\n",
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
