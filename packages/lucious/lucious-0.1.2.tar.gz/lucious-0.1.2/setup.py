from os import environ as envvars
from pathlib import Path
from setuptools import setup, find_packages


PROJECT_NAME = 'lucious'

setup(
    name=PROJECT_NAME,
    description='a chill tool for dealing with Snowflake',
    long_description=Path(__file__).absolute().parent.joinpath('README.md').read_text(),
    long_description_content_type='text/markdown',
    setup_requires=[
        'setuptools_scm==5.0.1'
    ],
    use_scm_version={'local_scheme': 'no-local-version'} if envvars.get('LOCAL_VERSION_SCHEME') else True,
    packages=find_packages(exclude=['tests']),
    author='Emmanuel I. Obi',
    maintainer='Emmanuel I. Obi',
    maintainer_email='withtwoemms@gmail.com',
    url=f'https://github.com/withtwoemms/{PROJECT_NAME}',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)

