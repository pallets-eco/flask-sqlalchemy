from pallets_sphinx_themes import get_version
from pallets_sphinx_themes import ProjectLink

# Project --------------------------------------------------------------

project = "Flask-SQLAlchemy"
copyright = "2010 Pallets"
author = "Pallets"
release, version = get_version("Flask-SQLAlchemy", version_length=1)

# General --------------------------------------------------------------

master_doc = "index"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "pallets_sphinx_themes",
    "sphinx_issues",
]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "flask": ("http://flask.pocoo.org/docs/", None),
    "sqlalchemy": ("https://docs.sqlalchemy.org/en/latest/", None),
}
issues_github_path = "pallets/werkzeug"

# HTML -----------------------------------------------------------------

html_theme = "flask"
html_context = {
    "project_links": [
        ProjectLink("Donate to Pallets", "https://palletsprojects.com/donate"),
        ProjectLink("Website", "https://palletsprojects.com/"),
        ProjectLink("PyPI releases", "https://pypi.org/project/Flask-SQLAlchemy/"),
        ProjectLink("Source Code", "https://github.com/pallets/flask-sqlalchemy/"),
        ProjectLink(
            "Issue Tracker", "https://github.com/pallets/flask-sqlalchemy/issues/"
        ),
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
html_title = "Flask-SQLAlchemy Documentation ({})".format(version)
html_show_sourcelink = False

# LaTeX ----------------------------------------------------------------

latex_documents = [
    (
        master_doc,
        "Flask-SQLAlchemy-{}.tex".format(version),
        html_title,
        author,
        "manual",
    )
]
