# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cyberpunk', 'cyberpunk.storage', 'cyberpunk.transformations']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.0.2,<3.0.0',
 'PyYAML>=6.0,<7.0',
 'boto3>=1.20.54,<2.0.0',
 'click>=8.0.3,<9.0.0',
 'gunicorn>=20.1.0,<21.0.0',
 'pydub>=0.25.1,<0.26.0',
 'python-dotenv>=0.19.2,<0.20.0',
 'requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['cyberpunk = main:main']}

setup_kwargs = {
    'name': 'cyberpunk',
    'version': '0.2.3',
    'description': 'Audio Processing Server',
    'long_description': '\n# Cyberpunk\n\nAudio Processing Server\n\n![GitHub](https://img.shields.io/github/license/jonaylor89/cyberpunk?logo=MIT) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/jonaylor89/cyberpunk/Docker)\n\n[![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run?git_repo=https://github.com/jonaylor89/cyberpunk)\n\n\n### Quick Start\n\n```sh\ndocker run -p 8080:8080 -e PORT=8080 ghcr.io/jonaylor89/cyberpunk:main\n```\n\nOriginal audio:\n```sh\nhttps://raw.githubusercontent.com/jonaylor89/cyberpunk/main/testdata/celtic_pt2.mp3\n```\n\n![](testdata/celtic_pt2.mp3)\n\n\nTry out the following audio URLs:\n```\nhttp://localhost:8000/unsafe/https://raw.githubusercontent.com/jonaylor89/cyberpunk/main/testdata/celtic_pt2.mp3\nhttp://localhost:8000/unsafe/https://raw.githubusercontent.com/jonaylor89/cyberpunk/main/testdata/celtic_pt2.mp3?reverse=true\nhttp://localhost:8000/unsafe/https://raw.githubusercontent.com/jonaylor89/cyberpunk/main/testdata/celtic_pt2.mp3?slice=0:10000\nhttp://localhost:8000/unsafe/https://raw.githubusercontent.com/jonaylor89/cyberpunk/main/testdata/celtic_pt2.mp3?reverse=true&repeat=1&slice=1000:5000\n\n```\n\n### Cyberpunk Endpoint\n\nCyberpunk endpoint is a series of URL parts which defines the image operations, followed by the image URI:\n\n```\n/HASH|unsafe/AUDIO?slice&concat&fade_in&fade_out&repeat&reverse&filters=NAME(ARGS)\n```\n\n- `HASH` is the URL Signature hash, or `unsafe` if unsafe mode is used\n- `slice`\n- `concat`\n- `fade_in`\n- `fade_out`\n- `repeat`\n- `reverse`\n- `AUDIO` is the audio URI\n\n\nCyberpunk provides utilities for previewing and generating Cyberpunk endpoint URI, including the [cyberpunk_path](https://github.com/jonaylor89/cyberpunk/tree/main/cyberpunk/processing.py) function and the `/params` endpoint:\n\n#### `GET /params`\n\nPrepending `/params` to the existing endpoint returns the endpoint attributes in JSON form, useful for preview:\n\n```sh\ncurl "http://localhost:8000/unsafe/celtic_p2.mp3?reverse=true&repeat=1&slice=1000:5000"\n\n{\n  "path": "/celtic_p2.mp3?reverse=true&repeat=1&slice=1000:5000"\n  "audio": "celtic_pt2.mp3",\n  "hash": "=",\n  "reverse": true,\n  "repeat": 1,\n  "slice": {\n      "start": 1000,\n      "end": 5000,\n  }\n}\n```\n\n# Features\n\n- [x] Audio Streaming\n\n- [x] Change encodings (e.g. mp3 -> wav)\n- [x] Audio slicing\n- [ ] Change Volume\n- [x] Concat Audio\n- [x] Repeat Audio\n- [x] Reverse Audio\n- [ ] Crossfade\n- [x] Fade in/out\n- [ ] Audio Quality\n- [ ] Audio Tagging\n- [ ] Audio Thumbnails\n- [ ] Mastering Music\n\n- [ ] Sound/Vocal Isolation\n\n- [ ] [Cool ML Stuff](https://github.com/spotify/pedalboard)\n\n- [ ] [File Caching](https://gist.github.com/ruanbekker/75d98a0d5cab5d6a562c70b4be5ba86d)\n\n# Storage Options\n\n- [x] Local\n- [ ] Cloud (e.g. S3)\n- [x] Blockchain (Audius)\n\n\n# Environment\n\nPORT: 8080 # server port number\n\nCYBERPUNK_SECRET: mysecret # secret key for URL signature\n\nAWS_ACCESS_KEY_ID: ...\n\nAWS_SECRET_ACCESS_KEY: ...\n\nAWS_REGION: us-east-1\n\nAUDIO_PATH=local:s3:audius:http\n\nSTORAGE_BASE_DIR=testdata/\n\nRESULTS_STORAGE_BASE_DIR=processed/\n\nS3_LOADER_BUCKET=mybucket\n\nS3_LOADER_BASE_DIR=audio/\n\nS3_STORAGE_BUCKET=mybucket\n\nS3_STORAGE_BASE_DIR=audio/\n\nS3_RESULTS_STORAGE_BUCKET=mybucket\n\nS3_RESULTS_STORAGE_BASE_DIR=audio/results\n\n\n# Docker Compose Example\n\nCyberpunk with file system, using mounted volumn:\n\n```yaml\nversion: "3"\nservices:\n  imagor:\n    image: jonaylor/cyberpunk:main\n    volumes:\n      - ./:/mnt/data\n    environment:\n      PORT: 8080\n      AUDIO_PATH: "local"\n      FILE_STORAGE_BASE_DIR: /mnt/data/testdata/ # enable file storage by specifying base dir\n    ports:\n      - "8080:8080"\n```\n\nCyberpunk with AWS S3:\n\n```yaml\nversion: "3"\nservices:\n  imagor:\n    image: jonaylor/cyberpunk:main\n    environment:\n      PORT: 8080\n      CYBERPUNK_SECRET: mysecret # secret key for URL signature\n      AWS_ACCESS_KEY_ID: ...\n      AWS_SECRET_ACCESS_KEY: ...\n      AWS_REGION: ...\n\n      AUDIO_PATH: "s3"\n\n      S3_LOADER_BUCKET: mybucket # enable S3 loader by specifying bucket\n      S3_LOADER_BASE_DIR: audio # optional\n\n      S3_STORAGE_BUCKET: mybucket # enable S3 storage by specifying bucket\n      S3_STORAGE_BASE_DIR: audio # optional\n\n      S3_RESULT_STORAGE_BUCKET: mybucket # enable S3 result storage by specifying bucket\n      S3_RESULT_STORAGE_BASE_DIR: audio/result # optional\n    ports:\n      - "8080:8080"\n```',
    'author': 'Johannes Naylor',
    'author_email': 'jonaylor89@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jonaylor89/cyberpunk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
