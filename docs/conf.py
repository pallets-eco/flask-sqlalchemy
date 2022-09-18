from pallets_sphinx_themes import get_version
from pallets_sphinx_themes import ProjectLink

# Project --------------------------------------------------------------

project = "Flask-SQLAlchemy"
copyright = "2010 Pallets"
author = "Pallets"
release, version = get_version("Flask-SQLAlchemy")

# General --------------------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "pallets_sphinx_themes",
    "sphinx_issues",
]
autodoc_typehints = "description"
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "flask": ("https://flask.palletsprojects.com/", None),
    "sqlalchemy": ("https://docs.sqlalchemy.org/", None),
}
issues_github_path = "pallets-eco/flask-sqlalchemy"

# HTML -----------------------------------------------------------------

html_theme = "flask"
html_context = {
    "project_links": [
        ProjectLink("Donate", "https://palletsprojects.com/donate"),
        ProjectLink("PyPI Releases", "https://pypi.org/project/Flask-SQLAlchemy/"),
        ProjectLink("Source Code", "https://github.com/pallets-eco/flask-sqlalchemy/"),
        ProjectLink(
            "Issue Tracker", "https://github.com/pallets-eco/flask-sqlalchemy/issues/"
        ),
        ProjectLink("Website", "https://palletsprojects.com/"),
        ProjectLink("Twitter", "https://twitter.com/PalletsTeam"),
        ProjectLink("Chat", "https://discord.gg/pallets"),
    ]
}
html_sidebars = {
    "index": ["project.html", "localtoc.html", "searchbox.html"],
    "**": ["localtoc.html", "relations.html", "searchbox.html"],
}
singlehtml_sidebars = {"index": ["project.html", "localtoc.html"]}
html_static_path = ["_static"]
html_favicon = "_static/flask-sqlalchemy-logo.png"
html_logo = "_static/flask-sqlalchemy-logo.png"
html_title = f"Flask-SQLAlchemy Documentation ({version})"
html_show_sourcelink = False
