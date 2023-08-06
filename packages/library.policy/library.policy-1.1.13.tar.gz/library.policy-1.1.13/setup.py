# -*- coding: utf-8 -*-
"""Installer for the library.policy package."""

from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CONTRIBUTORS.rst").read(),
        open("CHANGES.rst").read(),
    ]
)


setup(
    name="library.policy",
    version="1.1.13",
    description="Policy for the installation of buildout.library",
    long_description=long_description,
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: Addon",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone",
    author="Nicolas Demonte",
    author_email="support@imio.be",
    url="https://pypi.python.org/pypi/library.policy",
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["library"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        "plone.api>=1.8.4",
        "Products.GenericSetup>=1.8.2",
        "setuptools",
        "z3c.jbot",
        "eea.facetednavigation",
        "collective.big.bang",
        "collective.faceted.map",
        "collective.faceted.taxonomywidget",
        "collective.taxonomy",
        "plone.app.imagecropping",
        "plone.app.mosaic",
        "library.core",
        "library.theme",
        "collective.behavior.banner",
        "collective.behavior.gallery",
        "collective.easyform",
        "collective.preventactions",
        "collective.z3cform.select2",
        "collective.cookiecuttr",
        "iaweb.mosaic",
        "plone.formwidget.recaptcha",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            "plone.testing>=5.0.0",
            "plone.app.contenttypes",
            "plone.app.robotframework[debug]",
        ]
    },
    entry_points="""
    """,
)
