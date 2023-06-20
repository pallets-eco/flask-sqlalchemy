How to contribute to Flask-SQLAlchemy
=====================================

Thank you for considering contributing to Flask-SQLAlchemy!


Support questions
-----------------

Please don't use the issue tracker for this. The issue tracker is a tool
to address bugs and feature requests in Flask-SQLAlchemy itself. Use one
of the following resources for questions about using Flask-SQLAlchemy or
issues with your own code:

-   The ``#get-help`` channel on our Discord chat:
    https://discord.gg/pallets
-   The mailing list flask@python.org for long term discussion or larger
    issues.
-   Ask on `Stack Overflow`_. Search with Google first using:
    ``site:stackoverflow.com flask-sqlalchemy {search term, exception message, etc.}``

.. _Stack Overflow: https://stackoverflow.com/questions/tagged/flask-sqlalchemy?tab=Frequent


Reporting issues
----------------

Flask-SQLAlchemy is a thin wrapper that combines Flask and SQLAlchemy.
Make sure your issue is actually with Flask-SQLAlchemy and not
SQLAlchemy before submitting it. Check the traceback to see if the error
is coming from SQLAlchemy. Check if your issue has already been reported
to `SQLAlchemy`_.

Include the following information in your post:

-   Describe what you expected to happen.
-   If possible, include a `minimal reproducible example`_ to help us
    identify the issue. This also helps check that the issue is not with
    your own code.
-   Describe what actually happened. Include the full traceback if there
    was an exception.
-   List your Python, Flask-SQLAlchemy, and SQLAlchemy versions. If
    possible, check if this issue is already fixed in the latest
    releases or the latest code in the repository.

.. _SQLAlchemy: https://github.com/sqlalchemy/sqlalchemy/issues
.. _minimal reproducible example: https://stackoverflow.com/help/minimal-reproducible-example


Submitting patches
------------------

If there is not an open issue for what you want to submit, prefer
opening one for discussion before working on a PR. You can work on any
issue that doesn't have an open PR linked to it or a maintainer assigned
to it. These show up in the sidebar. No need to ask if you can work on
an issue that interests you.

Include the following in your patch:

-   Use `Black`_ to format your code. This and other tools will run
    automatically if you install `pre-commit`_ using the instructions
    below.
-   Include tests if your patch adds or changes code. Make sure the test
    fails without your patch.
-   Update any relevant docs pages and docstrings.
-   Add an entry in ``CHANGES.rst``. Use the same style as other
    entries. Also include ``.. versionchanged::`` inline changelogs in
    relevant docstrings.

.. _Black: https://black.readthedocs.io
.. _pre-commit: https://pre-commit.com


First time setup
~~~~~~~~~~~~~~~~

-   Download and install the `latest version of git`_.
-   Configure git with your `username`_ and `email`_.

    .. code-block:: text

        $ git config --global user.name 'your name'
        $ git config --global user.email 'your email'

-   Make sure you have a `GitHub account`_.
-   Fork Flask-SQLAlchemy to your GitHub account by clicking the `Fork`_
    button.
-   `Clone`_ the main repository locally, replacing ``{username}`` with your GitHub
    username.

    .. code-block:: text

        $ git clone https://github.com/{username}/flask-sqlalchemy
        $ cd flask-sqlalchemy

-   Create a virtualenv.

    .. code-block:: text

        $ python3 -m venv .venv
        $ . .venv/bin/activate

    On Windows, activating is different.

    .. code-block:: text

        > .venv\Scripts\activate

-   Install the development dependencies, then install Flask-SQLAlchemy
    in editable mode.

    .. code-block:: text

        $ pip install -r requirements/dev.txt && pip install -e .

-   Install the pre-commit hooks.

    .. code-block:: text

        $ pre-commit install

.. _latest version of git: https://git-scm.com/downloads
.. _username: https://docs.github.com/en/github/using-git/setting-your-username-in-git
.. _email: https://docs.github.com/en/github/setting-up-and-managing-your-github-user-account/setting-your-commit-email-address
.. _GitHub account: https://github.com/join
.. _Fork: https://github.com/pallets-eco/flask-sqlalchemy/fork
.. _Clone: https://docs.github.com/en/github/getting-started-with-github/fork-a-repo#step-2-create-a-local-clone-of-your-fork


Start coding
~~~~~~~~~~~~

-   Create a branch to identify the issue you would like to work on. If
    you're submitting a bug or documentation fix, branch off of the
    latest ".x" branch.

    .. code-block:: text

        $ git fetch origin
        $ git checkout -b your-branch-name origin/3.0.x

    If you're submitting a feature addition or change, branch off of the
    "main" branch.

    .. code-block:: text

        $ git fetch origin
        $ git checkout -b your-branch-name origin/main

-   Using your favorite editor, make your changes,
    `committing as you go`_.
-   Include tests that cover any code changes you make. Make sure the
    test fails without your patch. Run the tests as described below.
-   Push your commits to your fork on GitHub and
    `create a pull request`_. Link to the issue being addressed with
    ``fixes #123`` in the pull request.

    .. code-block:: text

        $ git push --set-upstream fork your-branch-name

.. _committing as you go: https://dont-be-afraid-to-commit.readthedocs.io/en/latest/git/commandlinegit.html#commit-your-changes
.. _create a pull request: https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request


Running the tests
~~~~~~~~~~~~~~~~~

Run the basic test suite with pytest.

.. code-block:: text

    $ pytest

This runs the tests for the current environment, which is usually sufficient. CI will
run the full suite when you submit your pull request. You can run the full test suite in
parallel with tox if you don't want to wait.

.. code-block:: text

    $ tox p


Running test coverage
~~~~~~~~~~~~~~~~~~~~~

Generating a report of lines that do not have test coverage can indicate where to start
contributing. Collect coverage from the tests and generate a report.

.. code-block:: text

    $ pip install "coverage[toml]"
    $ coverage run -m pytest
    $ coverage html

Open ``htmlcov/index.html`` in your browser to explore the report.

Read more about `coverage <https://coverage.readthedocs.io>`__.


Building the docs
~~~~~~~~~~~~~~~~~

Build the docs in the ``docs`` directory using Sphinx.

.. code-block:: text

    $ cd docs
    $ make html

Open ``_build/html/index.html`` in your browser to view the docs.

Read more about `Sphinx <https://www.sphinx-doc.org/en/stable/>`__.


Publishing a Release
--------------------

As a maintainer, once you decide it's time to publish a new release, follow these
instructions.

1.  You'll manage the release through a PR on GitHub. Create a branch like
    "release-A.B.C". For a fix release, branch off the corresponding release branch. For
    a feature release, branch off of main.

    .. code-block:: text

        $ git switch -c release-A.B.C A.B.x

2.  Review the ``CHANGES.rst`` file and ensure each code change has a corresponding
    entry. Only code changes need entries, not docs or non-published code and files. Use
    your judgement on what users would want to know.

3.  Update the ``CHANGES.rst`` file to replace "Unreleased" with "Released YYYY-MM-DD".

4.  Update ``__version__`` in ``__init__.py`` to remove the ".dev" suffix. Ensure that
    the version number matches what you think you're releasing.

5.  Commit with a standard message:

    .. code-block:: text

        $ git commit -am 'release version A.B.C'

6.  Push the branch and open a PR. The title should be the same as the commit message
    (if there was only one commit). No need to add a description. Assign it to the
    corresponding vesion milestone, like "3.0.4". If there's no milestone, it's because
    this is a newly adapted project that isn't using our full organization scheme yet,
    no problem.

7.  Don't merge the PR until the end. Observe that all workflows and checks pass for the
    PR.

8.  Create and push an annotated tag with a standard message. You'll see the new
    "build" workflow status get added to the PR checks.

    .. code-block:: text

        $ git tag -am 'release version A.B.C' A.B.C
        $ git push origin A.B.C

9.  Wait for the "build", "provenance", and "create-release" workflows to succeed. Go
    into the created draft release and check that the expected files (with the correct
    version numbers) are part of it. Add a quick message about the release, such as
    "This is a fix release for the 3.0.x release branch." along with a link to the
    changelog section and closed milestone. See an existing release in Flask for an
    example. Save the draft (don't publish it yet, it's not on PyPI yet.)

10. The "publish-pypi" workflow will have a yellow paused icon. A maintainer with
    publish permissions must approve it. Once they do, the release files will be
    uploaded to PyPI. If you don't have publish permission yet, ping the maintainers
    channel.

11. After seeing that the "publish-pypi" workflow succeeds, merge the PR. Then publish
    the draft release, and close the milestone.

12. If this was a fix release, merge the release branch (A.B.x) into main.

    .. code-block:: text

        $ git switch A.B.x
        $ git pull
        $ git switch main
        $ git merge A.B.x
        $ git push

    Here's how to handle the expected merge conflicts:

    * ``CHANGES.rst`` : Keep both changes, ensuring the next feature version is on top.
    * ``__init__.py`` : Keep the version in main (the next feature version).

12. If this was a feature release, make a new branch for fix releases.

    .. code-block:: text

        $ git switch main
        $ git pull
        $ git switch -c A.B.x
        $ git push

13. If this was a feature release, ask a maintainer with docs access to update Read the
    Docs to use the new branch as the primary.
