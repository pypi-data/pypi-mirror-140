from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='tremetrics',
    version='0.1.4',
    packages=['tremetrics'],
    url='https://gitlab.com/BCLegon/tremetrics',
    license='MIT',
    author='B.C. Legon',
    author_email='pypi@legon.it',
    description='Tremendous Metrics',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'numpy',
        'pytest',
        'scikit-learn',
    ]
)
