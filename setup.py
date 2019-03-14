from collections import OrderedDict
import io

from setuptools import setup

with io.open("README.rst", "rt", encoding="utf8") as f:
    README = f.read()


setup(
    name='Flask-SQLAlchemy',
    version='2.3.2',
    url='https://github.com/pallets/flask-sqlalchemy',
    project_urls=OrderedDict((
        ('Documentation', 'http://flask-sqlalchemy.pocoo.org/'),
        ('Code', 'https://github.com/pallets/flask-sqlalchemy'),
        ('Issue tracker', 'https://github.com/pallets/flask-sqlalchemy/issues'),
    )),
    license='BSD',
    author='Armin Ronacher',
    author_email='armin.ronacher@active-4.com',
    maintainer='Pallets team',
    maintainer_email='contact@palletsprojects.com',
    description='Adds SQLAlchemy support to your Flask application',
    long_description=README,
    packages=['flask_sqlalchemy'],
    zip_safe=False,
    platforms='any',
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    install_requires=[
        'Flask>=0.10',
        'SQLAlchemy>=0.8.0'
    ],
    test_suite='test_sqlalchemy.suite',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
