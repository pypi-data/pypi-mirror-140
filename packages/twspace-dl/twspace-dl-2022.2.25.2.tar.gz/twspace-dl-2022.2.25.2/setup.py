# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['twspace_dl']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['twspace_dl = twspace_dl.__main__:main']}

setup_kwargs = {
    'name': 'twspace-dl',
    'version': '2022.2.25.2',
    'description': 'The only tool to record Twitter spaces (yet)',
    'long_description': '<!-- markdownlint-disable MD033 MD041 -->\n\n<div align="center">\n  <h1 id="twspace-dl">Twspace-dl</h1>\n  <p>\n    <a href="https://pypi.org/project/twspace-dl/">\n      <img src="https://img.shields.io/pypi/v/twspace-dl?style=for-the-badge" alt="PyPI">\n    </a>\n    <a href="https://pypi.org/project/twspace-dl/">\n      <img src="https://img.shields.io/pypi/dm/twspace-dl?label=DOWNLOADS%20%28PYPI%29&amp;style=for-the-badge" alt="PyPI DLs">\n    </a>\n    <a href="https://github.com/Ryu1845/twspace-dl/releases">\n      <img src="https://img.shields.io/github/downloads/Ryu1845/twspace-dl/total?label=DOWNLOADS%20%28GITHUB%29&amp;style=for-the-badge" alt="Github Releases DLs">\n    </a>\n  </p>\n  <p>A python module to download twitter spaces.</p>\n</div>\n\n## Requirements\n\nffmpeg\n\n## Install\n\n### From portable binaries\n\n[Linux](https://github.com/Ryu1845/twspace-dl/releases/latest/download/twspace_dl.bin)\n\n[Windows](https://github.com/Ryu1845/twspace-dl/releases/latest/download/twspace_dl.exe)\n\n### From PyPI\n\n```bash\npip install twspace-dl\n```\n\n### From source\n\n```bash\ngit clone --depth 1 https://github.com/Ryu1845/twspace-dl\ncd twspace-dl\npip install .\n```\n\n## Usage\n\n```bash\ntwspace_dl -i space_url\n```\n\n<details>\n<summary>With binaries</summary>\n\n### Windows\n\n```bash\n.\\twspace_dl.exe -i space_url\n```\n\n### Linux\n\n```bash\n./twspace_dl.bin -i space_url\n```\n\n</details>\n\n## Features\n\nHere\'s the output of the help option\n\n```txt\nusage: twspace_dl [-h] [-v] [-s] [-k] [--input-cookie-file COOKIE_FILE] [-i SPACE_URL | -U USER_URL] [-d DYN_URL] [-f URL] [-M PATH] [-o FORMAT_STR] [-m] [-p] [-u] [--write-url URL_OUTPUT] {login} ...\n\nScript designed to help download twitter spaces\n\npositional arguments:\n  {login}               (EXPERIMENTAL) Login to your account using username and password\n\noptions:\n  -h, --help            show this help message and exit\n  -v, --verbose\n  -s, --skip-download\n  -k, --keep-files\n  --input-cookie-file COOKIE_FILE\n\ninput:\n  -i SPACE_URL, --input-url SPACE_URL\n  -U USER_URL, --user-url USER_URL\n  -d DYN_URL, --from-dynamic-url DYN_URL\n                        use the dynamic url for the processes(useful for ended spaces) \n                        example: https://prod-fastly-ap-northeast-1.video.pscp.tv/Transcoding/v1/hls/\n                        zUUpEgiM0M18jCGxo2eSZs99p49hfyFQr1l4cdze-Sp4T-DQOMMoZpkbdyetgfwscfvvUkAdeF-I5hPI4bGoYg/\n                        non_transcode/ap-northeast-1/periscope-replay-direct-prod-ap-northeast-1-public/\n                        audio-space/dynamic_playlist.m3u8?type=live\n  -f URL, --from-master-url URL\n                        use the master url for the processes(useful for ended spaces) \n                        example: https://prod-fastly-ap-northeast-1.video.pscp.tv/Transcoding/v1/hls/\n                        YRSsw6_P5xUZHMualK5-ihvePR6o4QmoZVOBGicKvmkL_KB9IQYtxVqm3P_vpZ2HnFkoRfar4_uJOjqC8OCo5A/\n                        non_transcode/ap-northeast-1/periscope-replay-direct-prod-ap-\n                        northeast-1-public/audio-space/master_playlist.m3u8\n  -M PATH, --input-metadata PATH\n                        use a metadata json file instead of input url (useful for very old ended spaces)\n\noutput:\n  -o FORMAT_STR, --output FORMAT_STR\n  -m, --write-metadata  write the full metadata json to a file\n  -p, --write-playlist  write the m3u8 used to download the stream(e.g. if you want to use another downloader)\n  -u, --url             display the master url\n  --write-url URL_OUTPUT\n                        write master url to file\n```\n## Format\n\nYou can use the following identifiers for the formatting\n\n```python\n%(title)s\n%(id)s\n%(start_date)s\n%(creator_name)s\n%(creator_screen_name)s\n%(url)s\n```\n\nExample: `[%(creator_screen_name)s]-%(title)s|%(start_date)s`\n\n## Known Errors\n\n`Changing ID3 metadata in HLS audio elementary stream is not implemented....`\n\nThis is an error in ffmpeg that does not affect twspace_dl at all as far as I\xa0know.\n\n## Service \n\nTo run as a systemd service please refer to https://github.com/Ryu1845/twspace-dl/blob/main/SERVICE.md\n\n## Docker\n\n### Run once\n\n> Use ${pwd} in powershell, or $(pwd) in bash\n\n```bash\ndocker run --rm -v ${pwd}:/output ryu1845/twspace-dl -i space_url\n```\n\n### Run as monitoring service\n\nUsing a cookie can help solve some problem with the twitter api. However, using one is not necessary.\n\n#### Without cookie\n\n1. Download the `docker-compose.yml`, `.env`, `monitor.sh` files and put them in a folder named `twspace-dl`.\n2. Edit `.env` and fill in the Twitter username you want to monitor.\n3. \\[Optional] If you want to used a cookies file, put it into the folder and named it `cookies.txt`.\n4. `docker-compose up -d`\n',
    'author': 'Ryu1845',
    'author_email': 'ryu@tpgjbo.xyz',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
