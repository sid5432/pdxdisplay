"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
    
# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
      name='pdxdisplay',
      version='0.0.1a2',
      
      description='Simple web application for viewing PDX (Product Data eXchange) XML files',
      long_description=long_description,
      url='https://github.com/sid5432/pdxdisplay',
      author='Sidney Li',
      author_email='sidneyli5432@gmail.com',
      classifiers=[  # Optional
                   # How mature is this project? Common values are
                   #   3 - Alpha
                   #   4 - Beta
                   #   5 - Production/Stable
                   'Development Status :: 3 - Alpha',
                   
                   # Indicate who your project is intended for
                   'Intended Audience :: Manufacturing',
                   'Topic :: Utilities',
                   
                   # Pick your license as you wish
                   'License :: OSI Approved :: Apache Software License',
                   
                   # Specify the Python versions you support here. In particular, ensure
                   # that you indicate whether you support Python 2, Python 3 or both.
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                  ],
      
      keywords='PDX package data exchange IPC IPC-2571 IPC-2570 Flask database postgreSQL sqlite3',
      
      # You can just specify package directories manually here if your project is
      # simple. Or you can use find_packages().
      #
      # Alternatively, if you just want to distribute a single Python file, use
      # the `py_modules` argument instead as follows, which will expect a file
      # called `my_module.py` to exist:
      #
      #   py_modules=["my_module"],
      #
      # packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required
      packages=find_packages(exclude=['archive','private','scripts']),
      
      install_requires=['flask','pypdx'],
      
      extras_require={
                      # 'dev': ['check-manifest'],
                      # 'test': ['pytest'],
                     },
      
      # this doesn't seem to be doing anything
      package_data={
                    'pdxdisplay': ['templates/*.html','static/stylesheets/*.css'],
                   },
      include_package_data=True,
      
      # To provide executable scripts, use entry points in preference to the
      # "scripts" keyword. Entry points provide cross-platform support and allow
      # `pip` to create the appropriate form of executable for the target
      # platform.
      #
      # For example, the following would provide a command called `sample` which
      # executes the function `main` from this package when invoked:
      entry_points={  # Optional
                    'console_scripts': [
                                        'pdxdisplay=pdxdisplay:main',
                                       ],
                   },
     )
