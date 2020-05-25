import io
import re

from setuptools import find_packages
from setuptools import setup

with io.open("README.rst", "rt", encoding="utf8") as f:
    readme = f.read()

with io.open("src/flask_sqlalchemy/__init__.py", "rt", encoding="utf8") as f:
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
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    python_requires=">= 3.6",
    install_requires=["Flask>=1.0.4", "SQLAlchemy>=1.2"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
