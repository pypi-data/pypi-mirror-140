#!/usr/bin/env python

import re


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


version = ''
with open('fc_tunnel/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')


with open('README.md', 'rb') as f:
    readme = f.read().decode('utf-8')

setup(
    name='fc_tunnel',
    version=version,
    description='Use FC to open up the tunnel between the local and Alibaba Cloud vpc network',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='xiliu',
    author_email='ls_huster@163.com',
    packages=['fc_tunnel'],
    install_requires=[
        'aliyun-fc2>=2.5.0',
        'alibabacloud-tunnel-service20210509',
        'retry'
    ],
    entry_points={
        'console_scripts': [
            'fct=fc_tunnel:run'
        ]
    },
    include_package_data=True,
    url='https://www.aliyun.com/product/fc',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ]
)