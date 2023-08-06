# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pydoc_markdown',
 'pydoc_markdown.contrib',
 'pydoc_markdown.contrib.loaders',
 'pydoc_markdown.contrib.processors',
 'pydoc_markdown.contrib.renderers',
 'pydoc_markdown.contrib.source_linkers',
 'pydoc_markdown.util']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.3,<6.0',
 'click>=7.1,<9.0',
 'databind>=1.5.0,<2.0.0',
 'docspec-python>=1.0.0,<2.0.0',
 'docspec>=1.0.0,<2.0.0',
 'docstring-parser>=0.11,<0.12',
 'nr.fs>=1.6.0,<2.0.0',
 'nr.stream>=0.1.2,<0.2.0',
 'requests>=2.23.0,<3.0.0',
 'toml>=0.10.1,<0.11.0',
 'watchdog']

entry_points = \
{'console_scripts': ['pydoc-markdown = pydoc_markdown.main:cli'],
 'pydoc_markdown.interfaces.Loader': ['python = '
                                      'pydoc_markdown.contrib.loaders.python:PythonLoader'],
 'pydoc_markdown.interfaces.Processor': ['crossref = '
                                         'pydoc_markdown.contrib.processors.crossref:CrossrefProcessor',
                                         'filter = '
                                         'pydoc_markdown.contrib.processors.filter:FilterProcessor',
                                         'google = '
                                         'pydoc_markdown.contrib.processors.google:GoogleProcessor',
                                         'pydocmd = '
                                         'pydoc_markdown.contrib.processors.pydocmd:PydocmdProcessor',
                                         'smart = '
                                         'pydoc_markdown.contrib.processors.smart:SmartProcessor',
                                         'sphinx = '
                                         'pydoc_markdown.contrib.processors.sphinx:SphinxProcessor'],
 'pydoc_markdown.interfaces.Renderer': ['docusaurus = '
                                        'pydoc_markdown.contrib.renderers.docusaurus:DocusaurusRenderer',
                                        'hugo = '
                                        'pydoc_markdown.contrib.renderers.hugo:HugoRenderer',
                                        'jinja2 = '
                                        'pydoc_markdown.contrib.renderers.jinja2:Jinja2Renderer',
                                        'markdown = '
                                        'pydoc_markdown.contrib.renderers.markdown:MarkdownRenderer',
                                        'mkdocs = '
                                        'pydoc_markdown.contrib.renderers.mkdocs:MkdocsRenderer'],
 'pydoc_markdown.interfaces.SourceLinker': ['bitbucket = '
                                            'pydoc_markdown.contrib.source_linkers.git:BitbucketSourceLinker',
                                            'git = '
                                            'pydoc_markdown.contrib.source_linkers.git:GitSourceLinker',
                                            'gitea = '
                                            'pydoc_markdown.contrib.source_linkers.git:GiteaSourceLinker',
                                            'github = '
                                            'pydoc_markdown.contrib.source_linkers.git:GithubSourceLinker',
                                            'gitlab = '
                                            'pydoc_markdown.contrib.source_linkers.git:GitlabSourceLinker']}

setup_kwargs = {
    'name': 'pydoc-markdown',
    'version': '4.5.1',
    'description': 'Create Python API documentation in Markdown format.',
    'long_description': '  [MkDocs]: https://www.mkdocs.org/\n\n![Python versions](https://img.shields.io/pypi/pyversions/pydoc-markdown?style=for-the-badge)\n[![Pypi version](https://img.shields.io/pypi/v/pydoc-markdown?style=for-the-badge)](https://pypi.org/project/pydoc-markdown/)\n[![Build status](https://img.shields.io/github/workflow/status/NiklasRosenstein/pydoc-markdown/Python%20package?style=for-the-badge)](https://github.com/NiklasRosenstein/pydoc-markdown/actions)\n[![Docs status](https://img.shields.io/readthedocs/pydoc-markdown?style=for-the-badge)](https://pydoc-markdown.readthedocs.io/en/latest/)\n\n# Pydoc-Markdown\n\nPydoc-Markdown is a tool and library to create Python API documentation in\nMarkdown format based on `lib2to3`, allowing it to parse your Python code\nwithout executing it.\n\nPydoc-Markdown requires Python 3.7 or newer, however the code that you want to\ngenerate API documentation for can be for any Python version.\n\n[>> Go to the Documentation](https://pydoc-markdown.readthedocs.io/en/latest/)\n\n## Features\n\n* Understands multiple doc styles (Sphinx, Google, Pydoc-Markdown)\n* Supports assignment docstrings (`#:` block before or string literal after the statement)\n* Links references to other documented API objects [WIP]\n* [MkDocs][], [Hugo](https://gohugo.io/) and [Docusaurus](https://v2.docusaurus.io/) integration\n\n## Installation\n\nInstall Pydoc-Markdown from PyPI:\n\n    $ pipx install \'pydoc-markdown>=4.0.0,<5.0.0\'\n\n## Quickstart (MkDocs)\n\n    $ pipx install mkdocs\n    $ pydoc-markdown --bootstrap mkdocs\n    $ pydoc-markdown --bootstrap readthedocs\n    $ pydoc-markdown --server --open\n\nWhat this does:\n\n1. Install [MkDocs][]\n2. Create a `pydoc-markdown.yml` file in the current directory\n3. Create files to render your documentation on [readthedocs.org](https://readthedocs.org/)\n4. Render Markdown files from the Python modules/packages in your current\n   working directory and run MkDocs to open a live-preview of the page.\n\n## Quickstart (Hugo)\n\n    $ pydoc-markdown --bootstrap hugo\n    $ pydoc-markdown --server --open\n  \nWhat this does:\n\n1. Create a `pydoc-markdown.yml` file in the current directory\n2. Render Markdown files from the Python modules/packages in your current working directory\n   and run Hugo to open a live-preview of the page. If Hugo is not available on your system,\n   it will be downloaded automatically.\n\n## Contributing to Pydoc-Markdown\n\nAll contributions are welcome! Check out the [Contributing](.github/CONTRIBUTING.md) guidelines.\n\n## Questions / Need help?\n\nFeel free to open a topic on [GitHub Discussions](https://github.com/NiklasRosenstein/pydoc-markdown/discussions)!\n\n---\n\n<p align="center">Copyright &copy; 2021 Niklas Rosenstein</p>\n',
    'author': 'Niklas Rosenstein',
    'author_email': 'rosensteinniklas@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
