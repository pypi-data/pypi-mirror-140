from setuptools import setup, find_packages
from package_viacep import viacep

with open('README.md', 'r') as red:
    page_description = red.read()

with open('requirements.txt', 'r') as req:
    requirements = req.read().splitlines()

setup(
    name='package_viacep',
    version=viacep.__version__,
    author='Antonio Oliveira',
    author_email='antoniobatistajr@gmail.com',
    description='Utility for Brazil zip code query or validation',
    long_description=page_description,
    long_description_content_type='text/markdown',
    url='https://github.com/antonioliverjr/package_viacep',
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)
