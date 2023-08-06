from setuptools import setup, find_packages

setup(
    name='radu_lib',
    version='0.1',
    packages=find_packages(),
    description= 'This is a test project!',
    author='eu',
    author_email='eu@toteu.com',
    url='https://google.com',
    istall_requires=['requests==2.24.0', 'pymongo', 'beautifulssoup4'],
    python_requires='>=3.10'
)