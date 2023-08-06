# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jgt_tools', 'jgt_tools.docs']

package_data = \
{'': ['*'], 'jgt_tools': ['data/*']}

install_requires = \
['tomli>=2.0.1,<3.0.0']

extras_require = \
{'build_docs': ['sphinx>=3.1.2',
                'sphinx-rtd-theme>=0.5.0',
                'ghp-import>=0.5.5'],
 'env_setup': ['pre-commit>=1.15'],
 'run_tests': ['pytest>=5.0']}

entry_points = \
{'console_scripts': ['build-and-push-docs = '
                     'jgt_tools.docs.build_docs:build_and_push[build_docs]',
                     'build-docs = jgt_tools.docs.build_docs:build[build_docs]',
                     'check-version = jgt_tools.check_version:check_version',
                     'env-setup = jgt_tools.env_setup:main',
                     'run-tests = jgt_tools.run_tests:main',
                     'self-check = jgt_tools.self_check:main']}

setup_kwargs = {
    'name': 'jgt-tools',
    'version': '0.6.0',
    'description': 'A collection of tools for commmon package scripts',
    'long_description': 'JGT Tools\n=========\n\nJGT Tools is a collection of package helpers\nfor common CLI functions\nwithin a properly-formatted repository.\n\n\nQuickstart\n----------\n\nJust include ``jgt_tools`` in your package VirtualEnv,\nand you\'ll have access to these CLI calls:\n\n- ``env-setup`` - set up the development environment\n  with all packages and pre-commit checks\n- ``self-check`` - run self-checks/linters/etc. on your repository\n- ``run-tests`` - run your in-repo test suite\n- ``build-docs`` - build repo documentation locally\n- ``build-and-push-docs`` - both build the docs,\n  then publish to your gh-pages branch\n- ``check-version`` - raise an error if package-relevant files have changed\n  without a version bump\n\nDetails for each script can be found by calling with the ``--help`` flag.\n\n.. tip::\n   In order to keep the environment as clean as possible,\n   JGT Tools will only install the libraries needed to start the tool itself.\n   However, several of the default commands\n   rely on additional libraries.\n   When ``env-setup`` is run for the first time,\n   it will check to see if each set of commands is still default,\n   and if so, install the libraries those commands need.\n\n\nrun-tests\n---------\nThe ``run-tests`` commands will\npass through any additional parameters\nprovided on the command line.\nFor example,\nby default ``run-tests`` maps to::\n\n    poetry run python -m pytest -vvv\n\nRunning ``run-tests -s`` would run::\n\n    poetry run python -m pytest -vvv -s\n\nDocumentation Index\n-------------------\n\nIn order to get the full benefit from ``build-docs``,\nit is encouraged to create an index file\nthat pulls together all the documentation.\nThis file needs to be in the root folder\nand should be called ``.jgt_tools.index``.\nThis will be moved into the working directory for Sphinx\nand be used when building the documentation.\nAdditional information can be found on the `Sphinx site`_.\n\nConfiguration\n-------------\n\nA number of the actions to be called\ncan be customized in a ``[tool.jgt_tools]``\nin your ``pyproject.toml`` file.\nAvailable values are:\n\n- ``env_setup_commands`` - a list of commands to be run\n  under the ``env-setup`` call\n- ``self_check_commands`` - a list of commands to be run\n  under the ``self-check`` call\n- ``run_tests_commands`` - a list of commands to be run\n  under the ``run-tests`` call\n- ``build_docs_commands`` - a list of commands to be run\n  under the ``build-docs`` call\n\nFor example::\n\n    [tool.jgt_tools]\n    env_setup_commands = [\n        "poetry install",\n        "poetry run pip install other_package",\n        "./my_custom_setup_script.sh"\n    ]\n    build_docs_commands = []\n\nwould run your specified commands for ``env-setup``\nand skip the default api doc builder.\n\n.. note::\n    NOTE: All commands provided in ``[tools.jgt_tools]``\n    will be run from project root.\n    To ensure your commands run as expected,\n    provide any paths in your custom commands relative from root.\n\nbuild_docs_commands\n~~~~~~~~~~~~~~~~~~~\n\nSpecifically for ``build_docs_commands``,\nthere are some variables\nthat can be used to aid in documentation building,\nusing Python-style curly-brace formatting::\n\n    BASE_DIR: Root library directory\n    PACKAGE_NAME: Folder name containing package\n    DOCS_WORKING_DIRECTORY: Temporary directory where docs are built (needed for Sphinx)\n    DOCS_OUTPUT_DIRECTORY: Final directory where docs are saved\n\nFor example::\n\n    [tool.jgt_tools]\n    build_docs_commands = [\n        "poetry run sphinx-apidoc --output-dir {DOCS_WORKING_DIRECTORY} --no-toc --force --module-first {PACKAGE_NAME}\n    ]\n\nbuilds the Sphinx API docs for the current package\nand stores the output files\nin the temporary working directory.\n\ncheck-version\n~~~~~~~~~~~~~\n\nIn addition,\nthe function to verify which files are relevant to ``check-version``\ncan be customized.\nBy default, if any files in the diff against master are ``.py`` files,\na version bump is expected,\nbut the user can provide an alternate function to verify filenames.\n\nThe function should expect a list of strings\nrepresenting file paths relative from project root\n(as provided by ``git diff master --name-only``)\nand return a boolean representing if a version change should be ensured\n(i.e. ``True`` if version should be checked).\n\nThis can be registered as a plugin in your ``pyproject.toml`` file::\n\n    [tools.poetry.plugins."file_checkers"]\n    "version_trigger" = "my_module:my_function"\n\nor in your ``setup.py`` file::\n\n    setup(\n        ...\n        entry_points={\n            "version_trigger": ["version_trigger = my_module:my_fuction"]\n        }\n    )\n\n.. _`Sphinx site`: http://www.sphinx-doc.org/en/master/usage/quickstart.html#defining-document-structure\n',
    'author': 'Brad Brown',
    'author_email': 'brad@bradsbrown.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://jolly-good-toolbelt.github.io/jgt_tools/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
