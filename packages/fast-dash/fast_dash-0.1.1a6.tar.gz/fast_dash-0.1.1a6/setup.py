# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fast_dash', 'tests']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.0.2,<3.0.0',
 'dash-bootstrap-components>=1.0.2,<2.0.0',
 'dash>=2.1.0,<3.0.0',
 'plotly>=5.5.0,<6.0.0']

extras_require = \
{'dev': ['tox>=3.20.1,<4.0.0',
         'virtualenv>=20.2.2,<21.0.0',
         'pip>=20.3.1,<21.0.0',
         'twine>=3.3.0,<4.0.0',
         'pre-commit>=2.12.0,<3.0.0',
         'toml>=0.10.2,<0.11.0'],
 'doc': ['mkdocs>=1.1.2,<2.0.0',
         'mkdocs-include-markdown-plugin>=1.0.0,<2.0.0',
         'mkdocs-material>=6.1.7,<7.0.0',
         'mkdocstrings>=0.13.6,<0.14.0',
         'livereload>=2.6.3,<3.0.0',
         'mkdocs-autorefs==0.1.1'],
 'test': ['black==20.8b1',
          'isort==5.6.4',
          'flake8==3.8.4',
          'flake8-docstrings>=1.6.0,<2.0.0',
          'pytest==6.1.2',
          'pytest-cov==2.10.1']}

setup_kwargs = {
    'name': 'fast-dash',
    'version': '0.1.1a6',
    'description': 'Create input-output web applications and user interfaces using Plotly Dash lightning fast..',
    'long_description': '# Overview\n\n\n<p align="center">\n<a href="https://pypi.python.org/pypi/fast_dash">\n    <img src="https://img.shields.io/pypi/v/fast_dash.svg"\n        alt = "Release Status">\n</a>\n\n<a href="https://github.com/dkedar7/fast_dash/actions">\n    <img src="https://github.com/dkedar7/fast_dash/actions/workflows/release.yml/badge.svg" alt="CI Status">\n</a>\n\n\n<a href="https://github.com/dkedar7/fast_dash/blob/main/LICENSE">\n    <img src="https://img.shields.io/github/license/dkedar7/fast_dash" alt="MIT License">\n</a>\n\n<a href="https://dkedar7.github.io/fast_dash/">\n    <img src="https://img.shields.io/badge/Docs-MkDocs-<COLOR>.svg" alt="Documentation">\n</a>\n\n</p>\n\n\n<p align="center">\n  <a href="https://dkedar7.github.io/fast_dash/"><img src="https://raw.githubusercontent.com/dkedar7/fast_dash/main/docs/assets/logo.png" alt="Fast Dash logo"></a>\n</p>\n<p align="center">\n    <em>Open source, Python-based tool to develop web applications lightining fast.</em>\n</p>\n\n\n---\n\n\n* Documentation: <https://dkedar7.github.io/fast_dash/>\n* Source code: <https://github.com/dkedar7/fast_dash/>\n\n---\n\nFast Dash is a Python module that makes the development of web applications fast and easy. It is built on top of Plotly Dash and can be used to build web interfaces for Machine Learning models or to showcase any proof of concept withoout the hassle of developing UI from scratch.\n\n## Simple example\n\nRun your app with three simple steps:\n\n```python\nfrom fast_dash.App import App\nfrom fast_dash.Components import TextInput, TextOutput\n\n# Step 1: Define your callback function\ndef callback_function(input_text):\n    # Code to process text\n    processed_text = input_text\n    return processed_text\n\n# Step 2: Specify the input/ output widgets\napp = App(callback_fn=callback_fn, \n        inputs=[TextInput()], \n        outputs=[TextOutput()], \n        title=\'My App\')\n\n# Step 3: Run your app!\napp.run()\n\n# * Running on http://127.0.0.1:8080/ (Press CTRL+C to quit)\n```\n\nOutput:\n\n![Simple example](https://raw.githubusercontent.com/dkedar7/fast_dash/main/docs/assets/simple_example.gif)\n\n## Features\n\n- No need to build UI from scratch\n- Launch an app only by specifying the types of inputs and outputs\n- Flask-based backend allows easy scalability and widespread compatibility\n- Option to customize per one\'s interest\n\nSome features are coming up in future releases:\n\n- More input and output components\n- Deploy to Heroku\n- and many more.\n\n## Community\n\nFast Dash is built on open-source. You are encouraged to share your own projects, which will be highlighted on a common community gallery that\'s upcoming. Join us on [Discord](https://discord.gg/B8nPVfPZ6a).\n\n## Credits\n\nFast Dash is build on top of [Plotly Dash](https://github.com/plotly/dash) and the documentation is inspired from [FastAPI\'s docs](https://fastapi.tiangolo.com/) project template. It is inpired from [gradio](https://github.com/gradio-app/gradio).',
    'author': 'Kedar Dabhadkar',
    'author_email': 'kdabhadk@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dkedar7/fast_dash',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
