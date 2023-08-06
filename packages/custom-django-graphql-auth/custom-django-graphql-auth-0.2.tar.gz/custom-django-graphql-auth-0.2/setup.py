from setuptools import setup, find_packages 


DESCRIPTION = 'This package contains patched packages for specific graphene_django, graphql_jwt and jwt versions to work with python 3.9'

#Setting up 
setup(
    name = "custom-django-graphql-auth",
    version= 0.2,
    Summary="Graphql and relay authentication with Graphene for Django.",
    author="Tinashe Chiraya",
    author_email="<shattyadrenal1@gmail.com>",
    maintainer= "Tinashe",
    description='This package contains patched packages for specific graphene_django, graphql_jwt and jwt versions to work with python 3.9 as well as prevent some dependency errors',
    license= "MIT",
    packages=find_packages(),
    classifiers=[
        'Operating System :: OS Independent',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
        'Framework :: Django',
    ],
    requires = [
        'Django (>=2.1.0)',
        'PyJWT (<2.0.0)',
        'graphene (>=2.1.8)',
        'black (==19.3b0)',
        'coveralls'
        ],
    zip_safe=False,
)