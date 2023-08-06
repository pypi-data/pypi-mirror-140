This library contains patched packages for specific graphene_django, graphql_jwt and jwt versions to work with python 3.9.
These packages are lower versions which are which are outdated on version 3.9 of python

how to create own package
start virtual env 
cd to directory
create setup.py file
create project folder
inside create __init__.py file and add code to call the py files in the folder
create files under project folder 
up in main folder when done
type pip install . to test 
if all is working 
type python setup.py sdist
your package will be created under the dist folder
pip install twine
then type twine upload dist/nameOfPackage.tar.gz
enter your credentials from pyPI 
and your package can now be installed world wide 