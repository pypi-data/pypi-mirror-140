#PreparePack

Repository that prepares packages directories and files

Installation:

    $ pip install preparepack

Usage:

    $ prepack -n packageName
    $ prepack --name packageName

Replace packageName with the name of your package. \
It will create the package directory named aspackageName_package,
the setup.py file, \
a subdirectory named packageName containing 
the __ _init_ __.py file and the package file named as packageName.py .

    $ buildpack 

Using this command you build the needed files before uploading your repository, such as .tar.gz and .whl .\
When you use this command, you must be in the same directory where the setup.py file is located.
