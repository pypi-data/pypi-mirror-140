# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['aws_service_availability']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0', 'rich>=10.14.0,<11.0.0', 'typer[all]>=0.4.0,<0.5.0']

extras_require = \
{':python_version < "3.8"': ['importlib_metadata>=4.5.0,<5.0.0']}

entry_points = \
{'console_scripts': ['aws-service-availability = '
                     'aws_service_availability.__main__:app']}

setup_kwargs = {
    'name': 'aws-service-availability',
    'version': '1.0.2',
    'description': 'CLI tool for listing (un)available AWS services by region',
    'long_description': '# aws-service-availability\n\n<div align="center">\n\n[![Build status](https://github.com/jensroland/aws-service-availability/workflows/build/badge.svg?branch=main&event=push)](https://github.com/jensroland/aws-service-availability/actions?query=workflow%3Abuild)\n[![Python Version](https://img.shields.io/pypi/pyversions/aws-service-availability.svg)](https://pypi.org/project/aws-service-availability/)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/jensroland/aws-service-availability/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n[![License](https://img.shields.io/github/license/jensroland/aws-service-availability)](https://github.com/jensroland/aws-service-availability/blob/main/LICENSE)\n![Coverage Report](assets/images/coverage.svg)\n\nCLI tool for listing (un)available AWS services by region, because the [AWS regional services page](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) no longer contains the useful table of supported services.\n\n</div>\n\n## 🚀 Features\n\n- List all the supported services for a given AWS region\n- List all the unsupported services for a given AWS region\n\n## Installation\n\n```bash\npip install -U aws-service-availability\n```\n\nor install with `Poetry`:\n\n```bash\npoetry add aws-service-availability\n```\n\nThen you can run the tool:\n\n```bash\naws-service-availability list-supported-services eu-north-1\naws-service-availability list-unsupported-services eu-north-1\n```\n\nor with `Poetry`:\n\n```bash\npoetry run aws-service-availability list-supported-services eu-north-1\npoetry run aws-service-availability list-unsupported-services eu-north-1\n```\n\n## 📈 Releases\n\nYou can see the list of available releases on the [GitHub Releases](https://github.com/jensroland/aws-service-availability/releases) page. We follow the [Semantic Versioning](https://semver.org/) specification.\n\n## 🛡 License\n\n[![License](https://img.shields.io/github/license/jensroland/aws-service-availability)](https://github.com/jensroland/aws-service-availability/blob/main/LICENSE)\n\nThis project is licensed under the terms of the `GNU GPL v3.0` license. See [LICENSE](https://github.com/jensroland/aws-service-availability/blob/main/LICENSE) for more details.\n\n## Credits\n\nThis project was generated with [`python-package-template`](https://github.com/JensRoland/python-package-template), based on [`python-package-template`](https://github.com/TezRomacH/python-package-template/) by Roman Tezikov.\n',
    'author': 'JensRoland',
    'author_email': 'mail@jensroland.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jensroland/aws-service-availability',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
