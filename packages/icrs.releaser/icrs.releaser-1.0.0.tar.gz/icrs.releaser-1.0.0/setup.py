# Copyright 2020 NextThought
# Released under the terms of the LICENSE file.
import codecs
from setuptools import setup, find_packages


version = '1.0.0'

entry_points = {
    'zest.releaser.prereleaser.before': [
        # XXX: This only works doing fullrelease
        'rm_cflags = icrs.releaser.removecflags:prereleaser_before',
    ],
    'zest.releaser.prereleaser.middle': [
        'version_next = icrs.releaser.versionreplacer:prereleaser_middle',
        # XXX: This only works doing fullrelease
        'scm_middle = icrs.releaser.setuptools_scm_versionfixer:prereleaser_middle',
    ],
    'console_scripts': [
        'icrs_release = icrs.releaser.fullrelease:main',
    ]
}

TESTS_REQUIRE = [
    'coverage',
    'zope.testrunner',
]

def _read(fname):
    with codecs.open(fname, encoding='utf-8') as f:
        return f.read()

setup(
    name='icrs.releaser',
    version=version,
    author='Jason Madden',
    author_email='jason@nextthought.com',
    description="zest.releaser/setuptools_scm plugin.",
    long_description=_read('README.rst') + '\n\n' + _read('CHANGES.rst'),
    license='Apache',
    keywords='zest.releaser release automation setuptools_scm git',
    url='https://github.com/jamadden/icrs.releaser',
    project_urls={
        'Documentation': 'https://icrsreleaser.readthedocs.io/en/latest/',
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Development Status :: 1 - Planning',
    ],
    zip_safe=False,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['icrs'],
    install_requires=[
        'setuptools',
        'setuptools_scm',
        'zest.releaser',
    ],
    entry_points=entry_points,
    include_package_data=True,
    extras_require={
        'test': TESTS_REQUIRE,
        'docs': [
            'Sphinx',
            'furo',
            'sphinxcontrib-programoutput',
        ] + TESTS_REQUIRE,
    },
    python_requires=">=3.8",
)
