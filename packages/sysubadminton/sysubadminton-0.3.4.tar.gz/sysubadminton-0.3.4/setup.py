#!/usr/bin/env python

from setuptools import setup
with open('./README.md', encoding='utf-8') as f:
    readme = f.read()
exec(open('./sysubadminton/version.py').read())

setup(
    name='sysubadminton',
    version=__version__,
    python_requires='>=3.6.0',
    author='SYSUBad',
    author_email='sysu@bad.com',
    url='https://gist.github.com/834e635e82739ee23d1450357f4fcc6e',
    description='用于中山大学珠海校区羽毛球场的预定',
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=['sysubadminton'],
    entry_points={
    'console_scripts': ['badminton=sysubadminton:main'],
    },
    install_requires=['requests', 'beautifulsoup4'],
    classifiers=[
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10'
    ],

)
