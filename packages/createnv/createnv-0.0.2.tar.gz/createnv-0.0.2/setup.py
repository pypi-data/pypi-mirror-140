# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['createnv']

package_data = \
{'': ['*']}

install_requires = \
['typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['createnv = createnv.cli:cli']}

setup_kwargs = {
    'name': 'createnv',
    'version': '0.0.2',
    'description': 'CLI to create .env files with environment variables.',
    'long_description': "# Createnv \n\n[![GitHub Actions: Tests](https://github.com/cuducos/createnv/workflows/Tests/badge.svg)]()\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/createnv)](https://pypi.org/project/createnv/)\n[![PyPI](https://img.shields.io/pypi/v/createnv)](https://pypi.org/project/createnv/)\n\nA simple CLI to create `.env` files.\n\n## Motivation\n\nI use `.env` file to decouple configuration from application in many projects, and I see that many newcomers might struggle in creating this file.\n\nThus, I created this package to offer a better user interface for creating configuration files in the format of `.env`.\n\n## Example\n\nUsing the sample `.env.sample` in this repository:\n\n[![asciicast](https://asciinema.org/a/311482.svg)](https://asciinema.org/a/311482)\n\nYou can now experiment by yourself, or try more advanced `.env.sample` such as the `tests/.env.sample` or [Bot Followers's `.env.sample`]\n\n## Install\n\nCreatenv requires [Python](https://python.org) 3.7 or newer:\n\n```console\n$ pip install createnv\n```\n\n## Usage\n\nTo use the default values (reads the sample from `.env.sample` and write the result into `.env`):\n\n```console\n$ createnv\n```\n\n### Options\n\n| Option | Default | Description |\n|---|---|---|\n| `--target` | `.env` | File to write the result |\n| `--source` | `.env.sample` | File to use as a sample |\n| `--overwrite` and `--no-overwrite` | `--no-overwrite` | Whether to ask before overwriting files\n| `--use-default` or `--no-use-default` | `--no-use-default` | Whether to ask for input on fields that have a default value set |\n| `--chars-for-random-string` | All ASCII letters, numbers and a few extra characters (`!@#$%^&*(-_=+)`) | Characters used to create random strings |\n\n## Format of sample files\n\nCreatenv reads the sample file and separate lines in blocks, splitting at empty lines. It follows a few rules:\n\n1. The first line is required to be a **title**\n2. The second line might be a **description** or a **variable**\n3. The remaining lines should be **variables**\n\n### Title\n\nThe first line of the block should start with a `#` character, followed by a space. The title value is the remaining text after the `#` and space.\n\n#### Example\n\n```\n# Hell Yeah!\n```\n\nIn this case, the title is _Hell yeah!_ (not _# Hell yeah!_).\n\n### Description (_optional_)\n\nIf the second line follows the syntax of a _title_ line, it's text (without the `# `) is considered a _description_ and is used to give more information to the user about the variables from this block.\n\n### Variables\n\nThere are three types of variables:\n\n#### Regular\n\nEach block might one or more variable lines. The syntax requires a _name of variable_ using only capital letters, numbers, or underscore, followed by an equal sign.\n\nWhat comes after the equal sign is _optional_. This text is considered the default value of this variable.\n\nThe human description of this variable is also _optional_. You can create one by placing a comment at the end of the line.  That is to say, any text after a sequence of **two spaces, followed by the `#` sign and one extra space**, is the human description of that variable.\n\n##### Example\n\n```\nNAME=\n```\n\nThis is a valid variable line. It has a name (_NAME_), no default value, and no human description. We can add a default value:\n\n```\nNAME=Cuducos\n```\n\nThis is still a valid variable line. It has a name(_NAME_), and a default value (_Cuducos_). Yet, we can add a human description:\n\n```\nNAME=Cuducos  # What is your name?\n```\n\nNow it's a complete variable with a name (_NAME_), a default value (_Cuducos_), and a human description (_What is your name?_)\n\n#### Random values\n\nIf you want to have a variable with a random value, you can set its default value to `<random>` and Createnv will take care of it. Optionally you can specify how long this variable should be with `:int`.\n\nYou can use the [`--chars-for-random-string` option](#options) to specify which characters to be used in the random value.\n\n##### Example\n\n```\nSECRET_KEY=<random>\nTOKEN=<random:32>\n```\n\nThe first line will create a `SECRET_VALUE` with random characters and random length between 64 and 128 chars.\n\nThe second line will create a `TOKEN` with random value and with exactly 32 characters.\n\n#### Auto generated\n\nFinally, you can combine existing variables _within the same block_ to create a new variable (without prompting your user to combine them), the syntax is similar to f-strings in Python..\n\n##### Example\n\n```\nNAME=  # What is your name?\nPERIOD=  # Is it morning, afternoon, or evening?\nGREETING=Good {PERIOD}, {NAME}!\n```\n\nIn this case, Createnv only asks the user for `NAME` and `PERIOD`, and creates `GREETING` automagically.\n",
    'author': 'Eduardo Cuducos',
    'author_email': 'cuducos@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cuducos/createnv',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
