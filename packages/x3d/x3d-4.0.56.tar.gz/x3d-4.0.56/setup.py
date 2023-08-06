"""
setup.py is configuration information for the *x3d* PyPi project.
"""

# https://docs.python.org/3/distutils/setupscript.html

import setuptools

DISTUTILS_DEBUG='verbose'

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="x3d",
    version="4.0.56", 
    author="Don Brutzman",
    author_email="brutzman@nps.edu",
    maintainer="Don Brutzman",
    maintainer_email="brutzman@nps.edu",
    description="Package support for Extensible 3D (X3D) Graphics International Standard (IS)",
### https://stackoverflow.com/questions/9977889/how-to-include-license-file-in-setup-py-script
    license_files = ('license.txt',),
    long_description=long_description,
    long_description_content_type="text/markdown",
#   download_url=""
    url="https://www.web3d.org/x3d/stylesheets/python/python.html",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10", # not 3.10.x
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Multimedia :: Graphics :: Presentation",
        "Topic :: Multimedia :: Graphics :: Viewers",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Text Processing :: Markup :: VRML",
    ],
    data_files=[
        ("examples",["examples/PythonX3dSmokeTests.py"])
    ],
    keywords=[
        "X3D","3D","graphics","Web3D"
    ],
###     "Topic :: Text Processing :: Markup :: X3D",
)

### package_dir={'x3d': 'dist/x3d'}, # testing...