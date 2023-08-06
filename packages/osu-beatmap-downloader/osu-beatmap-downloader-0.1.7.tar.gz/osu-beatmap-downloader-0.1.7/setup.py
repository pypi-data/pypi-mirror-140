# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['osu_beatmap_downloader']

package_data = \
{'': ['*']}

install_requires = \
['inquirerpy>=0.3.3,<0.4.0', 'loguru>=0.4.1,<0.5.0', 'requests>=2.23.0,<3.0.0']

entry_points = \
{'console_scripts': ['osu-beatmap-downloader = osu_beatmap_downloader:main']}

setup_kwargs = {
    'name': 'osu-beatmap-downloader',
    'version': '0.1.7',
    'description': 'Downloads x most favorized beatmapsets into the current directory',
    'long_description': "# Osu! Beatmapset Downloader\n\nDownloads given number of beatmapsets with the most favorites from [osu.ppy.sh](https://osu.ppy.sh/beatmapsets) into the default osu! directory.\n\n## Installation\n\nYou can install this program via `pip`:\n```\npip install osu-beatmap-downloader\n```\nThis will install the program in the global python package folder inside your python installation directory.\n\nYou can also install it into your python `user` directory with:\n```\npip install --user osu-beatmap-downloader\n```\n\nThese directories might not be in PATH. If you want to use this program from the command line, you may have to add the correct directories to PATH.\n\n## Usage\n\nTo use the downloader navigate to your osu! Songs directory (default is `C:\\<User>\\AppData\\Local\\osu!\\Songs\\`):\n```\ncd ~\\AppData\\Local\\osu!\\Songs\\\n```\n**Make sure you are in the correct directory** since the downloader will save all the files in the current working directory.\n\nThen start the dowloader with\n```\nosu-beatmap-downloader download\n```\nThe program will ask for your osu! username and password because [osu.ppy.sh](https://osu.ppy.sh/beatmapsets) won't let you download beatmaps without being logged in.\n\nThe program will then ask you if you want to save your credentials so that you don't have to enter them every time you want to start the program. They will be stored in `%USERPROFILE%/.osu-beatmap-downloader/credentials.json` on Windows and `~/.osu-beatmap-downloader/credentials.json` on Linux/macOS. The credentials are saved in **plaintext** (yes, that includes your password!). If you want to delete the credential file you can run:\n```\nosu-beatmap-downloader credentials --delete\n```\nYou can check if the credential file exists with:\n```\nosu-beatmap-downloader credentials --check\n```\n\nBy default the program will download the **top 200** beatmaps. You can change the limit with:\n```\nosu-beatmap-downloader download --limit 500\n```\nor\n```\nosu-beatmap-downloader download -l 500\n```\n\nYou can also download the beatmaps without video files by adding:\n```\nosu-beatmap-downloader download -l 500 --no-video\n```\nor\n```\nosu-beatmap-downloader download -l 500 -nv\n```\n\nThe programm will limit its rate to 30 files per minute to prevent unnecessary load on osu!s website.\nDespite this after a specific amount of songs (that I don't know) the website will prevent any further downloads. The program will terminate after 5 failed downloads. In this case **you might have to wait for half an hour or even longer** before you can download again.\n\nEvery step will be printed in your command line window and will also be logged in `%USERPROFILE%/.osu-beatmap-downloader/downloader.log` on Windows or `~/.osu-beatmap-downloader/downloader.log` on Linux/macOS.",
    'author': 'Vincent Mathis',
    'author_email': 'vincentmathis@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vincentmathis/osu-beatmap-downloader',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
