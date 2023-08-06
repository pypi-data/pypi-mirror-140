# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['commodore',
 'commodore.component',
 'commodore.component-template.hooks',
 'commodore.inventory',
 'commodore.postprocess']

package_data = \
{'': ['*'],
 'commodore': ['component-template/*',
               'component-template/{{ cookiecutter.slug }}/*',
               'component-template/{{ cookiecutter.slug }}/.github/*',
               'component-template/{{ cookiecutter.slug '
               '}}/.github/ISSUE_TEMPLATE/*',
               'component-template/{{ cookiecutter.slug }}/.github/workflows/*',
               'component-template/{{ cookiecutter.slug }}/class/*',
               'component-template/{{ cookiecutter.slug }}/component/*',
               'component-template/{{ cookiecutter.slug }}/docs/*',
               'component-template/{{ cookiecutter.slug '
               '}}/docs/modules/ROOT/pages/*',
               'component-template/{{ cookiecutter.slug '
               '}}/docs/modules/ROOT/pages/explanations/*',
               'component-template/{{ cookiecutter.slug '
               '}}/docs/modules/ROOT/pages/how-tos/*',
               'component-template/{{ cookiecutter.slug '
               '}}/docs/modules/ROOT/pages/references/*',
               'component-template/{{ cookiecutter.slug '
               '}}/docs/modules/ROOT/pages/tutorials/*',
               'component-template/{{ cookiecutter.slug '
               '}}/docs/modules/ROOT/partials/*',
               'component-template/{{ cookiecutter.slug }}/lib/*',
               'component-template/{{ cookiecutter.slug }}/tests/*',
               'component-template/{{ cookiecutter.slug '
               '}}/tests/golden/defaults/{{ cookiecutter.slug }}/apps/*',
               'filters/*',
               'lib/*']}

install_requires = \
['click',
 'cookiecutter',
 'gitpython',
 'importlib_metadata',
 'kapitan==0.30.0rc1',
 'python-dotenv',
 'requests',
 'typing-extensions>=3.7.4,<4.0.0',
 'url-normalize']

entry_points = \
{'console_scripts': ['autopep = tools.tools:autopep',
                     'commodore = commodore.cli:main',
                     'compile = tools.tools:compile',
                     'local_reveal = tools.tools:reveal']}

setup_kwargs = {
    'name': 'syn-commodore',
    'version': '0.14.1',
    'description': 'Commodore provides opinionated tenant-aware management of Kapitan inventories and templates. Commodore uses Kapitan for the heavy lifting of rendering templates and resolving a hierachical configuration structure.',
    'long_description': '# Project Syn: Commodore\n\nThis repository is part of Project Syn.\nFor documentation on Project Syn and this component, see https://syn.tools.\n\n**Please note that this project is in its early stages and under active development**.\n\nSee [GitHub Releases](https://github.com/projectsyn/commodore/releases) for changelogs of each release version of Commodore.\n\nSee [DockerHub](https://hub.docker.com/r/projectsyn/commodore) for pre-built\nDocker images of Commodore.\n\n## Overview\n\nCommodore provides opinionated tenant-aware management of\n[Kapitan](https://kapitan.dev/) inventories and templates. Commodore uses\nKapitan for the heavy lifting of rendering templates and resolving a\nhierachical configuration structure.\n\nCommodore introduces the concept of a component, which is a bundle of Kapitan\ntemplates and associated Kapitan classes which describe how to render the\ntemplates. Commodore fetches any components that are required for a given\nconfiguration before running Kapitan, and sets up symlinks so Kapitan can find\nthe component classes.\n\nCommodore also supports additional processing on the output of Kapitan, such\nas patching in the desired namespace for a Helm chart which has been rendered\nusing `helm template`.\n\n## System Requirements\n\n* Python 3.7, 3.8 or 3.9, with `python3-dev` and `python3-venv` updated\n* [jsonnet-bundler](https://github.com/jsonnet-bundler/jsonnet-bundler)\n\n## Getting started\n\n1. Recommended: create a new virtual environment\n    ```console\n    python3 -m venv venv\n    source venv/bin/activate\n    ```\n1. Install commodore from PyPI\n    ```console\n    pip install syn-commodore\n    ```\n1. <a name="getting_started_jsonnet"></a>Install jsonnet-bundler according to upstream [documentation](https://github.com/jsonnet-bundler/jsonnet-bundler#install).\n\n1. For Commodore to work, you need to run an instance of [Lieutenant](https://syn.tools/syn/tutorials/getting-started.html#_kickstart_lieutenant) somewhere\n   (locally is fine too).\n\n\n1. Setup a `.env` file to configure Commodore (don\'t use quotes):\n\n   ```shell\n   # URL of Lieutenant API\n   COMMODORE_API_URL=https://lieutenant-api.example.com/\n   # Lieutenant API token\n   COMMODORE_API_TOKEN=<my-token>\n   # Your local user ID to be used in the container (optional, defaults to root)\n   USER_ID=<your-user-id>\n   # Your username to be used in the commits (optional, defaults to your local git config)\n   COMMODORE_USERNAME=<your name>\n   # Your user email to be used in the commits (optional, defaults to your local git config)\n   COMMODORE_USERMAIL=<your email>\n   ```\n1. Run commodore\n    ```console\n    commodore\n    ```\n\n## Run Commodore with poetry\n\n### Additional System Requirements\n\n* [Poetry](https://github.com/python-poetry/poetry) 1.1.0+\n* Docker\n\n\n1. Install requirements\n\n   Install poetry according to the upstream\n   [documentation](https://github.com/python-poetry/poetry#installation).\n\n   Create the Commodore environment:\n\n    ```console\n    poetry install\n    ```\n\n    Install jsonnet-bundler according to upstream [documentation](https://github.com/jsonnet-bundler/jsonnet-bundler#install).\n\n\n1. Finish setup as described [above](#getting_started_jsonnet)\n\n1. Run Commodore\n\n   ```console\n   poetry run commodore\n   ```\n\n1. Start hacking on Commodore\n\n   ```console\n   poetry shell\n   ```\n\n   - Write a line of test code, make the test fail\n   - Write a line of application code, make the test pass\n   - Repeat\n\n   Note: Commodore uses the [Black](https://github.com/psf/black) code\n   formatter, and its formatting is encforced by CI.\n\n1. Run linting and tests\n\n   Auto format with autopep8\n   ```console\n   poetry run autopep\n   ```\n\n   List all Tox targets\n   ```console\n   poetry run tox -lv\n   ```\n\n   Run all linting and tests\n   ```console\n   poetry run tox\n   ```\n\n   Run just a specific target\n   ```console\n   poetry run tox -e py38\n   ```\n\n\n## Run Commodore in Docker\n\n**IMPORTANT:** After checking out this project, run `mkdir -p catalog inventory dependencies` in it before running any Docker commands. This will ensure the folders are writable by the current user in the context of the Docker container.\n\nA docker-compose setup enables running Commodore in a container.\nThe environment variables are picked up from the local `.env` file.\nBy default your `~/.ssh/` directory is mounted into the container and an `ssh-agent` is started.\nYou can skip starting an agent by setting the `SSH_AUTH_SOCK` env variable and mounting the socket into the container.\n\n1. Build the Docker image inside of the cloned Commodore repository:\n\n```console\ndocker-compose build\n```\n\n1. Run the built image:\n\n```console\ndocker-compose run commodore catalog compile $CLUSTER_ID\n```\n\n## Documentation\n\nDocumentation for this component is written using [Asciidoc][asciidoc] and [Antora][antora].\nIt is located in the [docs/](docs) folder.\nThe [Divio documentation structure](https://documentation.divio.com/) is used to organize its content.\n\nRun the `make docs-serve` command in the root of the project, and then browse to http://localhost:2020 to see a preview of the current state of the documentation.\n\nAfter writing the documentation, please use the `make docs-vale` command and correct any warnings raised by the tool.\n\n## Contributing and license\n\nThis library is licensed under [BSD-3-Clause](LICENSE).\nFor information about how to contribute see [CONTRIBUTING](CONTRIBUTING.md).\n\n[asciidoc]: https://asciidoctor.org/\n[antora]: https://antora.org/\n',
    'author': 'VSHN AG',
    'author_email': 'info@vshn.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/projectsyn/commodore',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
