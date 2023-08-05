# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aws_ddk',
 'aws_ddk.commands',
 'aws_ddk.data.project_templates.ddk_app.{{cookiecutter.directory_name}}',
 'aws_ddk.data.project_templates.ddk_app.{{cookiecutter.directory_name}}.{{cookiecutter.package_name}}',
 'aws_ddk.services']

package_data = \
{'': ['*'],
 'aws_ddk': ['data/cloudformation_templates/*',
             'data/project_templates/ddk_app/*']}

install_requires = \
['boto3>=1.20.37,<2.0.0',
 'botocore>=1.23.37,<2.0.0',
 'click>=8.0.3,<9.0.0',
 'cookiecutter>=1.7.3,<2.0.0']

entry_points = \
{'console_scripts': ['ddk = aws_ddk.__main__:main']}

setup_kwargs = {
    'name': 'aws-ddk',
    'version': '0.1.3',
    'description': 'AWS DataOps Development Kit - CLI',
    'long_description': '# AWS DataOps Development Kit (DDK) CLI\n\nCommand line interface to manage your DDK Apps.',
    'author': 'AWS Professional Services',
    'author_email': 'aws-proserve-opensource@amazon.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/awslabs/aws-ddk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
