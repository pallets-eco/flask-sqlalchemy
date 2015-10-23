"""
Flask-SQLAlchemy
----------------

Adds SQLAlchemy support to your Flask application.

Links
`````

* `documentation <http://flask-sqlalchemy.pocoo.org>`_
* `development version
  <http://github.com/mitsuhiko/flask-sqlalchemy/zipball/master#egg=Flask-SQLAlchemy-dev>`_

"""
from setuptools import setup


setup(
    name='Flask-SQLAlchemy',
    version='2.1',
    url='http://github.com/mitsuhiko/flask-sqlalchemy',
    license='BSD',
    author='Armin Ronacher',
    author_email='armin.ronacher@active-4.com',
    maintainer='Phil Howell',
    maintainer_email='phil@quae.co.uk',
    description='Adds SQLAlchemy support to your Flask application',
    long_description=__doc__,
    packages=['flask_sqlalchemy'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask>=0.10',
        'SQLAlchemy>=0.7'
    ],
    test_suite='test_sqlalchemy.suite',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ]
)
