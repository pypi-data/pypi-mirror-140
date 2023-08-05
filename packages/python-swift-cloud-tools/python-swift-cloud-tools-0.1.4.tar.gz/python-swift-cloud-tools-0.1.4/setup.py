# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

VERSION = __import__('swift_cloud_tools').__version__

setup(
    name='python-swift-cloud-tools',
    version=VERSION,
    description='Admin webapp for OpenStack Keystone and OpenStack Swift.',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    author='Storm',
    author_email='storm@g.globo',
    url='https://github.com/globocom/python-swift-cloud-tools',
    install_requires=[
        'requests==2.19.1'
    ],
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
)
