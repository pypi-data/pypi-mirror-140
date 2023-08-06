from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyselpom',
    version='1.2.3',
    packages=['pyselpom', 'helper'],
    url='https://github.com/c-pher/PySelenPOM',
    license='GNU General Public License v3.0',
    author='Andrey Komissarov',
    author_email='a.komisssarov@gmail.com',
    description='PySelPOM is a Page Object Model selenium based framework for humans.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'selenium>=4.1.0',
        'plogger==1.0.3',
    ],
    python_requires='>=3.9',
)
