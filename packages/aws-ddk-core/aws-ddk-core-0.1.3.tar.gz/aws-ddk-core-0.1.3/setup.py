# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aws_ddk_core',
 'aws_ddk_core.base',
 'aws_ddk_core.cicd',
 'aws_ddk_core.config',
 'aws_ddk_core.pipelines',
 'aws_ddk_core.resources',
 'aws_ddk_core.stages']

package_data = \
{'': ['*']}

install_requires = \
['aws-cdk-lib>=2.8.0,<3.0.0', 'marshmallow>=3.14.1,<4.0.0']

setup_kwargs = {
    'name': 'aws-ddk-core',
    'version': '0.1.3',
    'description': 'AWS DataOps Development Kit - Core',
    'long_description': '# AWS DataOps Development Kit (DDK) Core\n\nThe AWS DDK Core is a library of CDK constructs that you can use to build data workflows and modern data architecture on AWS, following our best practice.',
    'author': 'AWS Professional Services',
    'author_email': 'aws-proserve-opensource@amazon.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/awslabs/aws-ddk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
