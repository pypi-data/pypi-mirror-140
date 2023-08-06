# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '..'}

packages = \
['templateco']

package_data = \
{'': ['*'],
 'templateco': ['.mypy_cache/*',
                '.mypy_cache/3.7/*',
                '.mypy_cache/3.7/_pytest/*',
                '.mypy_cache/3.7/_pytest/_code/*',
                '.mypy_cache/3.7/_pytest/_io/*',
                '.mypy_cache/3.7/_pytest/assertion/*',
                '.mypy_cache/3.7/_pytest/config/*',
                '.mypy_cache/3.7/_pytest/mark/*',
                '.mypy_cache/3.7/_typeshed/*',
                '.mypy_cache/3.7/asyncio/*',
                '.mypy_cache/3.7/attr/*',
                '.mypy_cache/3.7/collections/*',
                '.mypy_cache/3.7/concurrent/*',
                '.mypy_cache/3.7/concurrent/futures/*',
                '.mypy_cache/3.7/ctypes/*',
                '.mypy_cache/3.7/email/*',
                '.mypy_cache/3.7/html/*',
                '.mypy_cache/3.7/importlib/*',
                '.mypy_cache/3.7/importlib_metadata/*',
                '.mypy_cache/3.7/iniconfig/*',
                '.mypy_cache/3.7/jinja2/*',
                '.mypy_cache/3.7/json/*',
                '.mypy_cache/3.7/logging/*',
                '.mypy_cache/3.7/makefun/*',
                '.mypy_cache/3.7/markupsafe/*',
                '.mypy_cache/3.7/multiprocessing/*',
                '.mypy_cache/3.7/os/*',
                '.mypy_cache/3.7/packaging/*',
                '.mypy_cache/3.7/pkg_resources/*',
                '.mypy_cache/3.7/prompt_toolkit/*',
                '.mypy_cache/3.7/prompt_toolkit/application/*',
                '.mypy_cache/3.7/prompt_toolkit/clipboard/*',
                '.mypy_cache/3.7/prompt_toolkit/completion/*',
                '.mypy_cache/3.7/prompt_toolkit/eventloop/*',
                '.mypy_cache/3.7/prompt_toolkit/filters/*',
                '.mypy_cache/3.7/prompt_toolkit/formatted_text/*',
                '.mypy_cache/3.7/prompt_toolkit/input/*',
                '.mypy_cache/3.7/prompt_toolkit/key_binding/*',
                '.mypy_cache/3.7/prompt_toolkit/key_binding/bindings/*',
                '.mypy_cache/3.7/prompt_toolkit/layout/*',
                '.mypy_cache/3.7/prompt_toolkit/lexers/*',
                '.mypy_cache/3.7/prompt_toolkit/output/*',
                '.mypy_cache/3.7/prompt_toolkit/shortcuts/*',
                '.mypy_cache/3.7/prompt_toolkit/shortcuts/progress_bar/*',
                '.mypy_cache/3.7/prompt_toolkit/styles/*',
                '.mypy_cache/3.7/prompt_toolkit/widgets/*',
                '.mypy_cache/3.7/py/*',
                '.mypy_cache/3.7/pyexpat/*',
                '.mypy_cache/3.7/pytest/*',
                '.mypy_cache/3.7/pytest_mock/*',
                '.mypy_cache/3.7/questionary/*',
                '.mypy_cache/3.7/questionary/prompts/*',
                '.mypy_cache/3.7/templateco/*',
                '.mypy_cache/3.7/unittest/*',
                '.mypy_cache/3.7/urllib/*',
                '.mypy_cache/3.7/xml/*',
                '.mypy_cache/3.7/xml/dom/*',
                '.mypy_cache/3.7/xml/parsers/*',
                '.mypy_cache/3.7/xml/parsers/expat/*',
                '.mypy_cache/3.7/xml/sax/*',
                'dist/*']}

install_requires = \
['Jinja2>=3,<4',
 'colorama>=0.4,<0.5',
 'importlib-metadata',
 'questionary>=1.10,<2.0',
 'typeguard>=2,<3',
 'typing-extensions>=4.0.1,<5.0.0']

setup_kwargs = {
    'name': 'templateco',
    'version': '0.1.6',
    'description': '',
    'long_description': '# Templateco\nAn ecosystem for generating customisable templated folders.\n\n## Getting Started\n```shell\n$ pip install templateco templateco-cli templateco-name-plugin\n# Successfully installed!\n\n$ templateco make template folder\n```\n\n1. This will install Templateco, the CLI and the terraform module.\n2. Create a Terraform folder called foo.\n\n## Interested in writing a plugin?\nRead the [PLUGIN.md](PLUGIN.md) documentation.\n',
    'author': 'Mike Gregory',
    'author_email': 'mike.ja.gregory@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
