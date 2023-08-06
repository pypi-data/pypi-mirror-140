from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='Larango',
    version='0.1.0',
    description='Larango Web Framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mosab-jbara/larango',
    author='Mosab Jbara',
    author_email='mosabjbara@gmail.com',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6, <4',
    install_requires=[
        'Django==4.0',
    ],
)
