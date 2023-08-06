# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['magnus_extension_aws_config']

package_data = \
{'': ['*']}

install_requires = \
['boto3', 'magnus']

setup_kwargs = {
    'name': 'magnus-extension-aws-config',
    'version': '0.1.0',
    'description': 'Magnus utility extension to provide AWS Configuration mixin',
    'long_description': '# Magnus AWS Configuration Mixin\n\nThis package provides the general AWS configuration methods used by services based on AWS.\n\nThis package is not meant to be used by its own but designed to be used as a dependency for actual AWS \nservice providers.\n\n## Installation instructions\n\n```pip install magnus_extension_aws_config```\n\n## Set up required to use the extension\n\nAccess to AWS environment either via:\n\n- AWS profile, generally stored in ~/.aws/credentials\n- AWS credentials available as environment variables\n\nIf you are using environmental variables for AWS credentials, please set:\n\n- AWS_ACCESS_KEY_ID: AWS access key\n- AWS_SECRET_ACCESS_KEY: AWS access secret\n- AWS_SESSION_TOKEN: The session token, useful to assume other roles\n\n\n## Config parameters\n\n### **aws_profile**:\n\nThe profile to use for acquiring boto3 sessions. \n\nDefaults to None, which is used if its role based access or in case of credentials present as environmental variables.\n\n### **region**:\n\nThe region to use for acquiring boto3 sessions.\n\nDefaults to *eu-west-1*.\n\n\n### **aws_credentials_file**:\n\nThe file containing the aws credentials.\n\nDefaults to ```~/.aws/credentials```.\n\n### **use_credentials**:\n\nSet it to ```True``` to provide AWS credentials via environmental variables.\n\nDefaults to ```False```.\n\n### ***role_arn***:\n\nThe role to assume after getting the boto3 session.\n\n**This is required if you are using ```use_credentials```.**\n',
    'author': 'Vijay Vammi',
    'author_email': 'vijay.vammi@astrazeneca.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/AstraZeneca/magnus-extension',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
