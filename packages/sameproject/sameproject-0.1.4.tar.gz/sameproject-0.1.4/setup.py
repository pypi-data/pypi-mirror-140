# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sameproject',
 'sameproject.backends',
 'sameproject.backends.aml',
 'sameproject.backends.common',
 'sameproject.backends.durable_functions',
 'sameproject.backends.durable_functions.execute_step',
 'sameproject.backends.durable_functions.execute_steps_workflow',
 'sameproject.backends.durable_functions.start_steps_workflow',
 'sameproject.backends.kubeflow',
 'sameproject.objects',
 'sameproject.program',
 'sameproject.program.compile',
 'sameproject.program.run',
 'sameproject.sdk',
 'sameproject.sdk.same',
 'sameproject.version']

package_data = \
{'': ['*'],
 'sameproject': ['templates/aml/*', 'templates/kubeflow/*'],
 'sameproject.backends.durable_functions': ['.vscode/*'],
 'sameproject.sdk': ['docs/*', 'experiment/*']}

install_requires = \
['Cerberus>=1.3.4,<2.0.0',
 'Jinja2>=3.0.1,<4.0.0',
 'click>=7,<8',
 'dill>=0.3.4,<0.4.0',
 'jupyter>=1.0.0,<2.0.0',
 'jupytext>=1.11.5,<2.0.0',
 'kfp>=1.8.2,<2.0.0',
 'kubernetes>=18.20.0,<19.0.0',
 'metakernel>=0.27.5,<0.28.0',
 'numpy>=1.21.2,<2.0.0',
 'pandas>=1.4.0,<2.0.0',
 'python-box>=5.4.1,<6.0.0',
 'regex>=2021.11.10,<2022.0.0',
 'requests>=2.26.0,<3.0.0',
 'ruamel.yaml==0.17.4',
 'tblib>=1.7.0,<2.0.0']

extras_require = \
{':extra == "azureml"': ['azureml-core>=1.37.0,<2.0.0'],
 ':sys_platform == "win32"': ['pywin32>=301']}

entry_points = \
{'console_scripts': ['same = sameproject.main:main']}

setup_kwargs = {
    'name': 'sameproject',
    'version': '0.1.4',
    'description': 'Notebooks to Pipelines, reproducible data science, oh my.',
    'long_description': None,
    'author': 'David Aronchick',
    'author_email': 'aronchick@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
