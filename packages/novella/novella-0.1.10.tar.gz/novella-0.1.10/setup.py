# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['novella', 'novella.markdown', 'novella.markdown.tags', 'novella.templates']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=4.0',
 'craftr-dsl>=0.7.7,<0.8.0',
 'markdown>=3.0.0,<4.0.0',
 'nr.util>=0.7.1',
 'tomli>=2.0.0,<3.0.0',
 'typing-extensions',
 'watchdog>=2.0.0,<3.0.0']

entry_points = \
{'console_scripts': ['novella = novella.__main__:main'],
 'novella.actions': ['copy-files = novella.action:CopyFilesAction',
                     'mkdocs-update-config = '
                     'novella.templates.mkdocs:MkdocsUpdateConfigAction',
                     'preprocess-markdown = '
                     'novella.markdown.preprocessor:MarkdownPreprocessorAction',
                     'run = novella.action:RunAction'],
 'novella.markdown.preprocessors': ['anchor = '
                                    'novella.markdown.tags.anchor:AnchorTagProcessor',
                                    'cat = '
                                    'novella.markdown.tags.cat:CatTagProcessor',
                                    'shell = '
                                    'novella.markdown.tags.shell:ShellTagProcessor'],
 'novella.templates': ['mkdocs = novella.templates.mkdocs:MkdocsTemplate']}

setup_kwargs = {
    'name': 'novella',
    'version': '0.1.10',
    'description': 'Linear build system for Markdown preprocessing and static site generation.',
    'long_description': '# novella\n\nNovella is a build system for processing files in a temporary directory isolated from the project source code. It is\ndesigned for the preprocessing of documentation source code such as Markdown files before they are passed into a\nstatic site generator such as [Mkdocs][] or [Hugo][]. Novella was designed as the backbone for [Pydoc-Markdown][],\nbut can be used independently.\n\n  [Mkdocs]: https://www.mkdocs.org/\n  [Hugo]: https://gohugo.io/\n  [Pydoc-Markdown]: https://github.com/NiklasRosenstein/pydoc-markdown\n  [Novella Documentation]: https://niklasrosenstein.github.io/novella\n\nCheck out the [Novella Documentation][] for more information.\n\n> Note: Novella is currently a work in progress project and is considered unstable.\n',
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
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
