# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['structure_factor', 'structure_factor.data']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.4.2,<4.0.0',
 'numba-scipy>=0.3.0,<0.4.0',
 'numba>=0.54.1,<0.55.0',
 'numpy>=1.20.3,<2.0.0',
 'pandas>=1.2.4,<2.0.0',
 'scipy>=1.6.2,<2.0.0',
 'spatstat-interface>=0.1.0,<0.2.0']

extras_require = \
{':python_version >= "3.5" and python_version < "3.8"': ['pickle5>0.0'],
 'docs': ['Sphinx>=4.0.3,<5.0.0',
          'sphinxcontrib-bibtex>=2.4.1,<3.0.0',
          'sphinxcontrib-proof>=1.3.0,<2.0.0',
          'rstcheck>=3.3.1,<4.0.0',
          'sphinx-rtd-theme>=1.0.0,<2.0.0'],
 'notebook': ['jupyter>=1.0.0,<2.0.0']}

setup_kwargs = {
    'name': 'structure-factor',
    'version': '2.0.1',
    'description': 'Approximate the structure factor of a stationary point process, test its effective hyperuniformity, and identify its class of hyperuniformity.',
    'long_description': "# structure-factor\n\n[![CI-tests](https://github.com/For-a-few-DPPs-more/structure-factor/actions/workflows/ci.yml/badge.svg)](https://github.com/For-a-few-DPPs-more/structure-factor/actions/workflows/ci.yml)\n[![codecov](https://codecov.io/gh/For-a-few-DPPs-more/structure-factor/branch/main/graph/badge.svg?token=FUDADJLO2W)](https://codecov.io/gh/For-a-few-DPPs-more/structure-factor)\n[![docs-build](https://github.com/For-a-few-DPPs-more/structure-factor/actions/workflows/docs.yml/badge.svg)](https://github.com/For-a-few-DPPs-more/structure-factor/actions/workflows/docs.yml)\n[![docs-page](https://img.shields.io/badge/docs-latest-blue)](https://for-a-few-dpps-more.github.io/structure-factor/)\n[![PyPi version](https://badgen.net/pypi/v/structure-factor/)](https://pypi.org/project/structure-factor/)\n[![Python >=3.7.1,<3.10](https://img.shields.io/badge/python->=3.7.1,<3.10-blue.svg)](https://www.python.org/downloads/release/python-371/)\n[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](./notebooks)\n\n> Approximate the structure factor of a stationary point process, test its effective hyperuniformity, and identify its class of hyperuniformity.\n\n- [structure-factor](#structure-factor)\n  - [Introduction](#introduction)\n  - [Dependencies](#dependencies)\n  - [Installation](#installation)\n    - [Install the project as a dependency](#install-the-project-as-a-dependency)\n    - [Install in editable mode and potentially contribute to the project](#install-in-editable-mode-and-potentially-contribute-to-the-project)\n  - [Documentation](#documentation)\n    - [Build the documentation](#build-the-documentation)\n  - [Getting started](#getting-started)\n    - [Documentation](#documentation-1)\n    - [Notebooks](#notebooks)\n\n## Introduction\n\n`structure-factor` is an open-source Python project which currently collects\n\n- various estimators of the structure factor,\n- and several diagnostics of hyperuniformity,\n\nfor stationary and isotropic point processes.\n\nPlease checkout the [documentation](https://for-a-few-dpps-more.github.io/structure-factor/) for more details.\n\n## Dependencies\n\n- [R programming language](https://www.r-project.org/), since we call the [`spatstat`](https://github.com/spatstat/spatstat) R package to estimate the pair correlation function of point processes using [`spatstat-interface`](https://github.com/For-a-few-DPPs-more/spatstat-interface).\n\n- Python dependencies are listed in the [`pyproject.toml`](./pyproject.toml) file.\n\n## Installation\n\n`structure-factor` works with [![Python >=3.7.1,<3.10](https://img.shields.io/badge/python->=3.7.1,<3.10-blue.svg)](https://www.python.org/downloads/release/python-371/).\n\nOnce installed it can be called from\n\n- `import structure_factor`\n- `from structure_factor import ...`\n\n### Install the project as a dependency\n\n- Install the latest version published on [![PyPi version](https://badgen.net/pypi/v/structure-factor/)](https://pypi.org/project/structure-factor/)\n\n  ```bash\n  # activate your virtual environment an run\n  poetry add structure-factor\n  # poetry add structure-factor@latest to update if already present\n  # pip install --upgrade structure-factor\n  ```\n\n- Install from source (this may be broken)\n\n  ```bash\n  # activate your virtual environment and run\n  poetry add git+https://github.com/For-a-few-DPPs-more/structure-factor.git\n  # pip install git+https://github.com/For-a-few-DPPs-more/structure-factor.git\n  ```\n\n### Install in editable mode and potentially contribute to the project\n\nThe package can be installed in **editable** mode using [`poetry`](https://python-poetry.org/).\n\nTo do this, clone the repository:\n\n- if you considered [forking the repository](https://github.com/For-a-few-DPPs-more/structure-factor/fork)\n\n  ```bash\n  git clone https://github.com/your_user_name/structure-factor.git\n  ```\n\n- if you have **not** forked the repository\n\n  ```bash\n  git clone https://github.com/For-a-few-DPPs-more/structure-factor.git\n  ```\n\nand install the package in editable mode\n\n```bash\ncd structure-factor\npoetry shell  # to create/activate local .venv (see poetry.toml)\npoetry install\n# poetry install --no-dev  # to avoid installing the development dependencies\n# poetry add -E docs -E notebook  # to install extra dependencies\n```\n\n## Documentation\n\nThe documentation [![docs-page](https://img.shields.io/badge/docs-latest-blue)](https://for-a-few-dpps-more.github.io/structure-factor/) is\n\n- generated using [Sphinx](https://www.sphinx-doc.org/en/master/index.html), and\n- published via the GitHub workflow file [.github/workflows/docs.yml](.github/workflows/docs.yml).\n\n### Build the documentation\n\nIf you use `poetry`\n\n- install the documentation dependencies (see `[tool.poetry.extras]` in [`pyproject.toml`](./pyproject.toml))\n\n  ```bash\n  cd structure-factor\n  poetry shell  # to create/activate local .venv (see poetry.toml)\n  poetry install -E docs  # (see [tool.poetry.extras] in pyproject.toml)\n  ```\n\n- and run\n\n  ```bash\n  # cd structure-factor\n  # poetry shell  # to create/activate local .venv (see poetry.toml)\n  poetry run sphinx-build -b html docs docs/_build/html\n  open _build/html/index.html\n  ```\n\nOtherwise, if you don't use `poetry`\n\n- install the documentation dependencies (listed in `[tool.poetry.extras]` in [`pyproject.toml`](./pyproject.toml)), and\n\n- run\n\n  ```bash\n  cd structure-factor\n  # activate a virtual environment\n  pip install '.[notebook]'  # (see [tool.poetry.extras] in pyproject.toml)\n  sphinx-build -b html docs docs/_build/html\n  open _build/html/index.html\n  ```\n\n## Getting started\n\n### Documentation\n\nSee the documentation [![docs-page](https://img.shields.io/badge/docs-latest-blue)](https://for-a-few-dpps-more.github.io/structure-factor/)\n\n### Notebooks\n\n[Jupyter](https://jupyter.org/) that showcase `structure-factor` are available in the [./notebooks](./notebooks) folder.\n\n<!--\n## How to cite this work\n\n### Companion paper\n\nA companion paper is being written\n\n> Exploring the hyperuniformity of a point process using structure-factor\n\nwhere we provide rigorous mathematical derivations of the different estimators of the structure factor and showcase `structure-factor` on three different point processes.\n\nIf you use `structure-factor`, please consider citing it with this piece of BibTeX:\n\n  ``` -->\n",
    'author': 'Diala Hawat',
    'author_email': 'dialahawat7@gmail.com',
    'maintainer': 'Diala Hawat',
    'maintainer_email': 'dialahawat7@gmail.com',
    'url': 'https://github.com/For-a-few-DPPs-more/structure-factor',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
