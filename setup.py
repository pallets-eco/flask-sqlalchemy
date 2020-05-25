import re

from setuptools import setup

with open("src/flask_sqlalchemy/__init__.py", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="Flask-SQLAlchemy",
    version=version,
    install_requires=["Flask>=1.0.4", "SQLAlchemy>=1.2"],
)
