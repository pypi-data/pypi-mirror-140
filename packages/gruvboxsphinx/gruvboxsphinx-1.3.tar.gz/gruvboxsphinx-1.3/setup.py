"""Python package configuration file."""
from io import open
from setuptools import setup
from gruvboxsphinx import __version__


with open("README.md") as readme_handle:
    readme = readme_handle.read()

setup(
    name='gruvboxsphinx',
    version=__version__,
    url='https://github.com/perpetualCreations/gruvbox-sphinx',
    license='MIT',
    author='perpetualCreations',
    description='Gruvbox-styled Sphinx HTML theme, forked from Insegel.',
    long_description=readme,
    long_description_content_type="text/markdown",
    zip_safe=False,
    packages=['gruvboxsphinx'],
    package_data={'gruvboxsphinx': [
        'theme.conf',
        '*.html',
        'static/css/*.css',
        'static/js/*.js',
        'static/img/*.*'
    ]},
    include_package_data=True,
    entry_points={
        'sphinx.html_themes': [
            'gruvboxsphinx = gruvboxsphinx',
        ]
    },
    classifiers=[
        'Framework :: Sphinx',
        'Framework :: Sphinx :: Theme',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
    ],
)
