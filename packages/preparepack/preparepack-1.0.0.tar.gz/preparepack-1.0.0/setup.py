from setuptools import setup
setup(
    name='preparepack',
    author='Cargo',
    version='1.0.0',
    packages=['prepack'],
    entry_points='''
    [console_scripts]
    prepack=prepack:prepack
    buildpack=prepack:build
    '''
)