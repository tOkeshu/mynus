#!python

# Import from the standard library
from setuptools import setup, find_packages

# Import from mynus
from mynus import __version__


setup( name             = "Mynus"
     , description      = "A minimalist and pure python wiki with no dependencies."
     , long_description = open("README.md").read()
     , license          = "GNU Affero General Public License v3 or later"

     , author           = "Romain Gauthier"
     , author_email     = "romain.gauthier@masteri2l.org"

     , version          = __version__
     , scripts          = ['bin/mynus']
     , packages         = ["mynus"]
     , package_data     = {'mynus': ['templates/*.html']}

     , classifiers      =
        [ "Development Status :: 3 - Alpha"
        , "License :: OSI Approved :: GNU Affero General Public License v3"
        , "Operating System :: OS Independent"
        , "Programming Language :: Python :: 2.6"
        , "Topic :: Utilities"
        ]
     )

