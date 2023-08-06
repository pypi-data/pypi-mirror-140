from setuptools import setup
from pathlib import Path

directory = Path(__file__).parent
longDescription = (directory/'README.md').read_text()

setup(
    name='preparepack',
    author='Cargo',
    version='1.1.0',
    packages=['prepack'],
    long_description=longDescription,
    long_description_content_type='text/markdown',
    entry_points='''
    [console_scripts]
    prepack=prepack:prepack
    buildpack=prepack:build
    '''
)