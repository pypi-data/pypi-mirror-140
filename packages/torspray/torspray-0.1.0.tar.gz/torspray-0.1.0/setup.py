"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')


setup(
    name='torspray',
    version='0.1.0',
    description='A console utility to bring up new Tor bridges easily',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gergelykalman/torspray',
    author='Gergely Kalman',
    author_email='g@gergelykalman.com',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3.10",
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='tor, tor-bridge, automation, provisioning',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6, <4',
    install_requires=[
        'paramiko',
    ],
    extras_require={},
    package_data={},
    entry_points={
        'console_scripts': [
            'torspray=torspray:main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/gergelykalman/torspray/issues',
        'Say Thanks!': 'https://twitter.com/gergely_kalman',
        'Source': 'https://github.com/gergelykalman/torspray',
    },
)
