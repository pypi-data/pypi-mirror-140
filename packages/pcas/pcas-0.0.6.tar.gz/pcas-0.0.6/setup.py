"""Setup file for pypi upload."""

# To use this, remove 
# python3 setup.py sdist bdist_wheel

# To the extent possible under law, the author(s) have dedicated all copyright and
# related and neighboring rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
# 
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

import setuptools

with open('README.md') as f:
    README = f.read()

setuptools.setup(
    author='Tom Coates, Alexander Kasprzyk',
    author_email='t.coates@imperial.ac.uk',
    name='pcas',
    license='CC0',
    description='pcas provides an interface to PCAS microservices.',
    version='0.0.6',
    long_description=README,
    long_description_content_type = 'text/markdown',
    url='https://bitbucket.org/pcas/python-interface',
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    install_requires=[
        'grpcio',
        'protobuf',
        ],
    classifiers=[
        # Trove classifiers
        # (https://pypi.python.org/pypi?%3Aaction=list_classifiers)
        'Development Status :: 4 - Beta',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Database :: Front-Ends',
        'Topic :: System :: Logging',
        'Programming Language :: SQL',
    ],
)