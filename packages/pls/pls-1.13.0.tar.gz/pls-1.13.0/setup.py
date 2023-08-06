# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pls',
 'pls.config',
 'pls.constants',
 'pls.data',
 'pls.enums',
 'pls.fs',
 'pls.models',
 'pls.models.mixins',
 'pls.output']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'rich>=11.1.0,<12.0.0']

entry_points = \
{'console_scripts': ['pls = pls.main:main']}

setup_kwargs = {
    'name': 'pls',
    'version': '1.13.0',
    'description': '`pls` is a prettier `ls` for the pros.',
    'long_description': '<h1 align="center">\n  <img height="128px" src="https://raw.githubusercontent.com/dhruvkb/pls/main/readme_assets/pls.svg"/>\n</h1>\n\n<p align="center">\n  <a href="https://pypi.org/project/pls/">\n    <img src="https://img.shields.io/pypi/v/pls" alt="pls on PyPI"/>\n  </a>\n  <a href="https://www.python.org">\n    <img src="https://img.shields.io/pypi/pyversions/pls" alt="Python versions"/>\n  </a>\n  <a href="https://github.com/dhruvkb/pls/blob/main/LICENSE">\n    <img src="https://img.shields.io/github/license/dhruvkb/pls" alt="GPL-3.0"/>\n  </a>\n  <a href="https://pypi.org/project/pls/">\n    <img src="https://img.shields.io/static/v1?label=supported%20OS&message=posix,%20win&color=informational" alt="Platforms"/>\n  </a>\n  <a href="https://dhruvkb.github.io/pls/">\n    <img src="https://img.shields.io/static/v1?label=docs&message=dhruvkb/pls:docs&color=informational" alt="Docs"/>\n  </a>\n  <a href="https://github.com/dhruvkb/pls/actions/workflows/ci.yml">\n    <img src="https://github.com/dhruvkb/pls/actions/workflows/ci.yml/badge.svg" alt="CI status"/>\n  </a>\n</p>\n\n<p align="center">\n  <img src="https://raw.githubusercontent.com/dhruvkb/pls/main/readme_assets/demo.png" alt="Demo of `pls`"/>\n</p>\n\n`pls` is a prettier `ls` for the pros.\n\nThe "p" stands for\n- pretty (the output from `pls` surely looks better)\n- programmer (`pls` is geared towards developers)\n- professional (`pls` can be extensively tweaked by the pros)\n- Python (`pls` is written in Python!)\n\nJust pick whichever helps you remember the command name.\n\nIt works in a manner similar to `ls`, in  that it lists directories and files in\na given directory, but it adds many more\n[developer-friendly features](https://dhruvkb.github.io/pls/features).\n\n> ⚠️ Note that `pls` is not a replacement for `ls`. `ls` is a tried, tested and\ntrusted command with lots of features. `pls`, on the other hand, is a simple\ntool for people who just want to see the contents of their directories.\n\n## Documentation\n\nWe have some very beautiful [documentation](https://dhruvkb.github.io/pls) over\non our GitHub pages site. These docs are built from the\n[`docs` branch](https://github.com/dhruvkb/pls/tree/docs) in the same\nrepository, so contributions to the docs are most welcome.\n\nThe docs contain information on almost everything, including but not limited to\nthe following:\n\n- [installation, updates and usage](https://dhruvkb.github.io/pls/get_started)\n- [features and CLI options](https://dhruvkb.github.io/pls/features)\n- [reference](https://dhruvkb.github.io/pls/reference)\n- [contribution](https://dhruvkb.github.io/pls/contribution)\n\n---\n\n🚧 Everything below this line will eventually be transferred to the\n[documentation](https://dhruvkb.github.io/pls).\n\n## Features\n\n`pls` provides many features over  `ls` command. `pls` can:\n\n- show Nerd Font icons or emoji next to files and directories making it easier to read the output\n- colour output to elevate important files or dim unimportant ones\n- use a more nuanced approach to hidden files than plainly hiding files with a leading dot `.`\n- group directories and shows them all before files\n- ignore leading dots `.` and normalise case when sorting files\n- align files names by first character\n- show technical two-letter Git status for files and directories\n- cascade formatting rule specs by based on specificity levels\n- read [`.pls.yml`](.pls.yml) files from the directory to augment its configuration\n- show more details like permissions, owner and size in columns\n- link files and hide derived files behind the main ones\n\nThe icon, color and most behaviour in the application can be [configured using\nplain-text YAML files](src/pls/data/README.md) for the pros who prefer to tweak\ntheir tools.\n\n## Upcoming features\n\nIn the future `pls` will be able to\n\n- generate visibility rules by parsing `.gitignore`\n- add MIME type as another method for matching files to specs\n- use complete path based matching for files\n- generate tree-like output for subdirectories\n\nIf you want to help implement any of these features, feel free to submit a PR.\n`pls` is free and open-source software.\n\n## Comparison with similar tools\n\nThere are a lot of `ls` replacements. Here are some of the most popular ones.\n\n- [`exa`](https://github.com/ogham/exa)\n- [`lsd`](https://github.com/Peltoche/lsd)\n- [`colorls`](https://github.com/athityakumar/colorls)\n- [`ls-go`](https://github.com/acarl005/ls-go)\n\n`pls` aims to stand out because of some very specific choices.\n\n- Does not intend to replace `ls`. `pls`, as a command, is just as easy to type.\n- Targets a more tech-savvy audience in its [features](#features).\n- Intelligently [maps file type](src/pls/data/README.md). Just comparing the file extension would be too generic.\n- Meticulously chosen iconography for the appreciating eyes.\n- Highly customisable at a project level using a simple [`.pls.yml`](.pls.yml) file.\n- Built in a friendly language, Python. This makes it easy to fork and change it yourself.\n',
    'author': 'Dhruv Bhanushali',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://dhruvkb.github.io/pls',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
