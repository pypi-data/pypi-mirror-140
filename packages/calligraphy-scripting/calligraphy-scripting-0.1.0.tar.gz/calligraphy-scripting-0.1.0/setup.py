# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['calligraphy_scripting', 'calligraphy_scripting.data']

package_data = \
{'': ['*']}

install_requires = \
['rich>=11.2.0,<12.0.0']

entry_points = \
{'console_scripts': ['calligraphy = calligraphy_scripting.cli:cli']}

setup_kwargs = {
    'name': 'calligraphy-scripting',
    'version': '0.1.0',
    'description': 'A hybrid language for a modern approach to shell scripting',
    'long_description': "# Calligraphy\n---\n[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n\n**Shell scripting for the modern age**\n\nCalligraphy is a hybrid scripting language that allows you to mix Python and Bash code\nin the same file. This gives you the advantages of bash when working with other\nprocesses while also giving you the advantages of a modern language like Python.\n\nIt's a free software distributed under the MIT Licence unless\notherwise specified.\n\nDevelopment is hosted on GitHub: https://github.com/jfcarter2358/calligraphy/\n\nPull requests are amazing and most welcome.\n\n## Install\n\nCalligraphy can be simply installed by running\n\n```\npip install calligraphy-scripting\n```\n\nIf you want to install from a source distribution, extract the tarball and run\nthe following command (this requires poetry to be installed)\n\n```\npoetry install --no-dev\n```\n\n## Documentation\n\nThe documentation lives at https://calligraphy.readthedocs.io/.\n\n## Testing\n\nWe use `pytest` and `pytest-cov` for running the test suite. You should be able to install them with\n\n```\npip install pytest pytest-cov\n```\n\nor you can install calligraphy alongside those packages with\n\n```\npoetry install\n```\n\nTo run the test suite, you can do\n\n```\nmake test\n```\n\nThis will produce an html coverage report under the `htmlcov` directory.\n\n## Roadmap\n\n### v1.0.0\n\n- [x] Add indentation to explain output\n    - When using the explain flag the resulting annotated code isn't indented. This can make it hard to read considering that indentation matters in Python and Calligraphy, so we should include that in our output.\n- [x] Reference environment variables from Bash lines with `env.NAME` pattern instead of `${NAME}`\n    - Right now we get/set env variables from the Python side of things in one way and access them in a different way from Bash. This isn't ideal as it can cause confusion with two ways of doing things, so we should standardize.\n- [ ] Enable sourcing of other calligraphy scripts\n    - In order to make Calligraphy more useful, we need to end the limitation of only one source file. A `source` directive should be introduced which allows other Calligraphy scripts to be imported.\n- [ ] Token output flag\n    - It's useful to be able to see the token representaion of a source file when debugging, therefore we should add a flag which outputs said representation.\n- [ ] Use `$N` where N is an integer greater than 0 for arguments\n    - Right now we need to use `sys.argv[N]` in order to access arguments. This isn't much of an issue, but it's slightly clunky. We'd like to be able to denote program arguments in the same way Bash does.\n\n### v1.1.0\n\n- [ ] Windows shell support\n    - Currently when a shell command is run it adds `printenv` at the end in order to capture environment changes. We need to detect which OS is being run on and use `set` in its place on Windows.\n\n## License\n\nCalligraphy is under the [MIT license](https://opensource.org/licenses/MIT).\n\n## Contact\n\nIf you have any questions or concerns please reach out to me (John Carter) at [jfcarter2358@gmail.com](mailto:jfcarter2358@gmail.com)\n",
    'author': 'John Carter',
    'author_email': 'jfcarter2358@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jfcarter2358/calligraphy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
