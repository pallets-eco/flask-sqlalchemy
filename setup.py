import io
import re

from setuptools import setup

with io.open("README.rst", "rt", encoding="utf8") as f:
    readme = f.read()

with io.open("flask_sqlalchemy/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read(), re.M).group(1)

setup(
    name="Flask-SQLAlchemy",
    version=version,
    url="https://github.com/pallets/flask-sqlalchemy",
    project_urls={
        "Documentation": "https://flask-sqlalchemy.palletsprojects.com/",
        "Code": "https://github.com/pallets/flask-sqlalchemy",
        "Issue tracker": "https://github.com/pallets/flask-sqlalchemy/issues",
    },
    license="BSD-3-Clause",
    author="Armin Ronacher",
    author_email="armin.ronacher@active-4.com",
    maintainer="Pallets",
    maintainer_email="contact@palletsprojects.com",
    description="Adds SQLAlchemy support to your Flask application.",
    long_description=readme,
    packages=["flask_sqlalchemy"],
    include_package_data=True,
    python_requires=">= 2.7, != 3.0.*, != 3.1.*, != 3.2.*, != 3.3.*",
    install_requires=["Flask>=0.10", "SQLAlchemy>=0.8.0"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
