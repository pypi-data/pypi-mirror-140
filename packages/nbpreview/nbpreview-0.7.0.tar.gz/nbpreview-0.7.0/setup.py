# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nbpreview',
 'nbpreview.component',
 'nbpreview.component.content',
 'nbpreview.component.content.output',
 'nbpreview.component.content.output.result',
 'nbpreview.data']

package_data = \
{'': ['*'], 'nbpreview': ['templates/*']}

install_requires = \
['Jinja2>=3.0.1,<4.0.0',
 'Pillow>=8.3.1,<10.0.0',
 'Pygments>=2.10.0,<3.0.0',
 'click-help-colors>=0.9.1,<0.10.0',
 'html2text>=2020.1.16,<2021.0.0',
 'httpx>=0.19,<0.23',
 'ipython>=7.27,<9.0',
 'lxml>=4.6.3,<5.0.0',
 'markdown-it-py>=1.1,<3.0',
 'mdit-py-plugins>=0.3.0,<0.4.0',
 'nbformat>=5.1.2,<6.0.0',
 'picharsso>=2.0.1,<3.0.0',
 'pylatexenc>=2.10,<3.0',
 'rich>=10.9.0,<11.0.0',
 'terminedia>=0.4.1,<0.5.0',
 'typer>=0.4.0,<0.5.0',
 'types-click>=7.1.5,<8.0.0',
 'validators>=0.18.2,<0.19.0',
 'yarl>=1.6.3,<2.0.0']

entry_points = \
{'console_scripts': ['nbp = nbpreview.__main__:app',
                     'nbpreview = nbpreview.__main__:app']}

setup_kwargs = {
    'name': 'nbpreview',
    'version': '0.7.0',
    'description': 'nbpreview',
    'long_description': "<!-- title-start -->\n\n![nbpreview light logo](https://github.com/paw-lu/nbpreview/blob/main/docs/_static/images/logo_light.svg#gh-light-mode-only)\n![nbpreview dark logo](https://github.com/paw-lu/nbpreview/blob/main/docs/_static/images/logo_dark.svg#gh-dark-mode-only)\n\n# nbpreview\n\n<!-- title-end -->\n\n<!-- non-https-badges-start -->\n\n[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)\n\n<!-- non-https-badges-end -->\n\n[![PyPI](https://img.shields.io/pypi/v/nbpreview.svg)](https://pypi.org/project/nbpreview/)\n[![Status](https://img.shields.io/pypi/status/nbpreview.svg)](https://pypi.org/project/nbpreview/)\n[![Python Version](https://img.shields.io/pypi/pyversions/nbpreview)](https://pypi.org/project/nbpreview)\n[![License](https://img.shields.io/pypi/l/nbpreview)](https://opensource.org/licenses/MIT)\n[![Read the documentation at https://nbpreview.readthedocs.io/](https://img.shields.io/readthedocs/nbpreview/latest.svg?label=Read%20the%20Docs)][documentation]\n[![Tests](https://github.com/paw-lu/nbpreview/workflows/Tests/badge.svg)](https://github.com/paw-lu/nbpreview/actions?workflow=Tests)\n[![Codecov](https://codecov.io/gh/paw-lu/nbpreview/branch/main/graph/badge.svg)](https://codecov.io/gh/paw-lu/nbpreview)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![tryceratops](https://img.shields.io/badge/try%2Fexcept%20style-tryceratops%20%F0%9F%A6%96%E2%9C%A8-black)](https://github.com/guilatrova/tryceratops)\n[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)\n\nA terminal viewer for Jupyter notebooks.\nIt's like [cat](https://man7.org/linux/man-pages/man1/cat.1.html)[^cat] for ipynb files.\n\n[^cat]: No, _nbpreview does not actually concatenate files_—but it does print them.\n\n[documentation]: https://nbpreview.readthedocs.io/\n\n<!-- github-only -->\n\n![Hero image](https://github.com/paw-lu/nbpreview/blob/main/docs/_static/images/hero_image.png)\n\n## Documentation\n\nnbpreview's [documentation] contains\na detailed breakdown of its [features],\n[command-line usage][usage],\nand [instructions on how to configure][configure] the tool.[^documentation]\n\n## Features\n\nnbpreview can:\n\n- [Syntax highlight code cells](https://nbpreview.readthedocs.io/en/latest/features.html#syntax-highlighting)\n- [Render markdown](https://nbpreview.readthedocs.io/en/latest/features.html#markdown-rendering)\n- [Draw images](https://nbpreview.readthedocs.io/en/latest/features.html#images)\n- [Render DataFrame](https://nbpreview.readthedocs.io/en/latest/features.html#dataframe-rendering)\n- [Create previews for Vega charts](https://nbpreview.readthedocs.io/en/latest/features.html#vega-and-vegalite-charts)\n- [Render LaTeX](https://nbpreview.readthedocs.io/en/latest/features.html#latex)\n- [Parse HTML](https://nbpreview.readthedocs.io/en/latest/features.html#html)\n- [Create hyperlinks for complex content](https://nbpreview.readthedocs.io/en/latest/features.html#hyperlinks)\n- [Use Nerd Font icons](https://nbpreview.readthedocs.io/en/latest/features.html#nerd-fonts)\n- [Render stderr output](https://nbpreview.readthedocs.io/en/latest/features.html#stderr)\n- [Render tracebacks](https://nbpreview.readthedocs.io/en/latest/features.html#tracebacks)\n\n## Requirements\n\n- Python 3.8+\n\n## Installation\n\n<!-- installation-start -->\n\nnbpreview can be installed through [pipx] or [pip] from [PyPI](https://pypi.org/).\n\n[pipx] provides an easy way to install Python applications in isolated environments.\n[See the documentation for how to install pipx.](https://pypa.github.io/pipx/installation/#install-pipx)\n\n```console\n% pipx install nbpreview\n```\n\nIf [pipx] is not installed,\nnbpreview may also be installed via [pip]:\n\n```console\n% python -m pip install nbpreview\n```\n\n[pipx]: https://pypa.github.io/pipx/\n[pip]: https://pip.pypa.io/\n\n<!-- installation-end -->\n\n## Usage\n\nTo use nbpreview,\nsimply type `nbpreview` into your terminal followed by the path of the notebook you wish to view.\n\n```console\n% nbpreview notebook.ipynb\n```\n\nSee the [command-line reference][usage] for details on options.\n\n## Contributing\n\nContributions are very welcome.\nTo learn more, see the [contributor guide][contributing].\n\n## License\n\nDistributed under the terms of the [MIT license][license],\n_nbpreview_ is free and open source software.\n\n## Issues\n\nIf you encounter any problems,\nplease [file an issue][issues] along with a detailed description.\n\n## Prior art\n\n### Similar tools\n\n<!-- similar-tools-start -->\n\nThanks to [@joouha] for [maintaining a list of these tools][euporie_similar_tools].\nMany of the projects here were found directly on their page.\n\n- [ipynb-term](https://github.com/PaulEcoffet/ipynbviewer)\n- [ipynbat](https://github.com/edgarogh/ipynbat)\n- [ipynbviewer](https://github.com/edgarogh/ipynbat)\n- [jcat](https://github.com/ktw361/jcat)\n- [jupview](https://github.com/Artiomio/jupview)\n- [jupytui](https://github.com/mosiman/jupytui)\n- [jut](https://github.com/kracekumar/jut)\n- [nbcat](https://github.com/jlumpe/nbcat)\n- [nbtui](https://github.com/chentau/nbtui)\n- [nbv](https://github.com/lepisma/nbv)\n- [Read-Jupyter-Notebook](https://github.com/qcw171717/Read-Jupyter-Notebook)\n\n[@joouha]: https://github.com\n[euporie_similar_tools]: https://euporie.readthedocs.io/en/latest/pages/related.html#notebook-viewers\n\n<!-- similar-tools-end -->\n\n### Complimentary tools\n\n<!-- complimentary-tools-start -->\n\nIf you're interested in complimentary tools\nthat help improve the terminal experience for notebooks,\nthere are many amazing projects out there.\n\n- **[bat](https://github.com/sharkdp/bat)**\n  is not a tool for notebooks specifically.\n  But similar to nbpreview,\n  it provides a rich output for many types of files on the terminal,\n  and is the primary inspiration for nbpreview.\n- **[euporie]**\n  is a really exciting project\n  that allows you to edit and run Jupyter notebooks on the terminal.\n- **[nbclient]**\n  is a library for executing notebooks from the command line.\n- **[nbqa]**\n  allows the use of linters and formatters on notebooks.\n  It's also used by this project.\n- **[jpterm]**\n  is and up-and-coming successor to [nbterm]\n  which will be accompanied by a web client.\n  Looking forward to seeing this develop.\n- **[nbtermix]**\n  is an actively-developed fork of [nbterm].\n- **[nbterm]**\n  lets you edit and execute Jupyter Notebooks on the terminal.\n- **[papermill]**\n  allows the parameterization and execution of Jupyter Notebooks.\n\n[nbterm]: https://github.com/davidbrochart/nbterm\n[euporie]: https://github.com/joouha/euporie\n[nbclient]: https://github.com/jupyter/nbclient\n[nbqa]: https://github.com/nbQA-dev/nbQA\n[jpterm]: https://github.com/davidbrochart/jpterm\n[nbtermix]: https://github.com/mtatton/nbtermix\n[papermill]: https://github.com/nteract/papermill\n\n<!-- complimentary-tools-end -->\n\n## Credits\n\n<!-- credits-start -->\n\nnbpreview relies on a lot of fantastic projects.\nCheck out the [dependencies] for a complete list of libraries that are leveraged.\n\nBesides the direct dependencies,\nthere are some other projects that directly enabled the development of nbpreview.\n\n- **[bat]**\n  is not explicitly used in this project,\n  but served as the primary inspiration.\n  This projects strives to be [bat]—but\n  for notebooks.\n  Many of nbpreview's features and command-line options are directly adopted from [bat].\n- **[Hypermodern Python Cookiecutter]**\n  is the template this project was generated on.\n  It is a fantastic project that integrates [Poetry],\n  [Nox],\n  and [pre-commit].\n  It's responsible for most of this project's CI.\n- **[justcharts]**\n  is directly used by this project\n  to generate the Vega and Vega-Lite charts.\n\n[bat]: https://github.com/sharkdp/bat\n[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n[justcharts]: https://github.com/koaning/justcharts\n[nox]: https://nox.thea.codes/en/stable/\n[poetry]: https://python-poetry.org/\n[pre-commit]: https://pre-commit.com/\n\n<!-- credits-end -->\n\n[^documentation]: Thanks to [Furo], [MyST], and [Rich][exporting_rich_console].\n\n[configure]: https://nbpreview.readthedocs.io/configure.html\n[contributing]: https://github.com/paw-lu/nbpreview/blob/main/CONTRIBUTING.md\n[dependencies]: https://github.com/paw-lu/nbpreview/blob/main/pyproject.toml\n[exporting_rich_console]: https://rich.readthedocs.io/en/stable/console.html#exporting\n[features]: https://nbpreview.readthedocs.io/features.html\n[furo]: https://pradyunsg.me/furo/quickstart/\n[issues]: https://github.com/paw-lu/nbpreview/issues\n[license]: https://opensource.org/licenses/MIT\n[myst]: https://myst-parser.readthedocs.io/en/latest/\n[usage]: https://nbpreview.readthedocs.io/en/latest/usage.html\n",
    'author': 'Paulo S. Costa',
    'author_email': 'Paulo.S.Costa5@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/paw-lu/nbpreview',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.0,<4.0.0',
}


setup(**setup_kwargs)
