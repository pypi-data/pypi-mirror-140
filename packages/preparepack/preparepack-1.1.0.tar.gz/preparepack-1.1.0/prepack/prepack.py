import click, os, subprocess

@click.command()
@click.option('--name', '-n', help='Name of the package to be prepared.', required=True)
def prepack(name):
    os.system(f'mkdir {name}_package')
    with open(f'{name}_package/setup.py', 'w') as set:
        set.write(f'from setuptools import setup\n\nsetup(\n    name=\'{name}\',\n    author=\'\',\n    version=\'1.0.0\',\n    packages=[\'{name}\'],\n    entry_points=\'\'\'\'\'\'\n)')

    os.system(f'mkdir {name}_package/{name}')
    with open(f'{name}_package/{name}/__init__.py', 'w') as ini:
        ini.write(f'from .{name} import *')

    with open(f'{name}_package/{name}/{name}.py', 'w') as file:
        file.write('')

@click.command()
def build():
    os.system('pip install .')
    os.system('python setup.py sdist bdist_wheel')