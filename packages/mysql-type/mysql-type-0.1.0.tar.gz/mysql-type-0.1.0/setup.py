from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='mysql-type',
    version='0.1.0',
    py_modules=['mysql_type'],
    url='https://github.com/antialize/py-mysql-type',
    author='Jakob Truelsen',
    author_email='antialize@gmail.com',
    description='Functions and types to facilitate mysql typed queries',
    long_description=readme(),
    license='Apache',
    install_requires=[
        'markdown',
    ],
)
