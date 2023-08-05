# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cvraft']

package_data = \
{'': ['*'], 'cvraft': ['templates/*']}

install_requires = \
['Jinja2>=3.0.3,<4.0.0',
 'Markdown>=3.3.6,<4.0.0',
 'beautifulsoup4>=4.10.0,<5.0.0',
 'python-frontmatter>=1.0.0,<2.0.0',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['cvraft = cvraft.cli:app']}

setup_kwargs = {
    'name': 'cvraft',
    'version': '0.1.2',
    'description': 'Build your CV written in Markdown',
    'long_description': '# Cvraft\n\nInstead of writing your CV or resumé in Microsoft Word, Google Docs, or some proprietary tools, you can just write it in Markdown. As a Markdown file is just plain text, you can easily track version with Git or your VCS of choice. Copy and paste with ease.\n\n**cvraft** transforms your Markdown file to a ready-to-use HTML file. You can also [customize it with ease](#customization).\n\n## Install\n\n```bash\npip install cvraft\n```\n\n## Usage\n\nOutput HTML file to a **build** directory in current directory. It also copies **static** directory (if it exists in the same directory as the source Markdown file) to **build**.\n\n```bash\ncvraft build <path/to/file.md>\n```\n\nView the HTML file in a local web server at http://localhost:9000\n\n```bash\ncvraft serve\n```\n\n## Customization\n\nThe different with standard Markdown tool is that the output HTML is tweaked to wrap different parts of your CV in proper **section** tags. This will ease your cutomization with CSS.\n\nThe generated HTML structure could look like this\n\n![HTML structure](./docs/images/html-structure.png)\n\nWith this structure, you can write your custom CSS in the **static/styles/main.css**. This path is the default CSS path in the generated HTML file.',
    'author': 'Manh-Ha VU',
    'author_email': 'dev@manhhavu.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cvraft/cvraft',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
