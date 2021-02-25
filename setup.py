#!/usr/bin/env python

"""
Prerequesites -
  Python Packages:
    * setuptools
    * GitPython
  System Packages:
    * make
    * Python 3
Commands: python setup.py [bdist_wheel / [sdist [--format=[gztar][,zip][,tar]]]
Ex:
  * python setup.py bdist_wheel
  * python setup.py sdist
  * python setup.py sdist --format=gztar
  * python setup.py sdist --format=zip
  * python setup.py sdist --format=tar
  * python setup.py sdist --format=gztar,tar,zip
  * python setup.py sdist --format=gztar,zip
  * python setup.py bdist_wheel sdist --format=gztar,zip,tar
"""

"""
distutils/setuptools install script.
"""


from setuptools import setup, find_packages
import traceback
import shutil
import re
import os
__NAME__ = "flask-cognito-auth"

ROOT = os.path.dirname(os.path.abspath(__file__))
VERSION_FILE = os.path.join(ROOT, __NAME__.replace("-", "_"), ".version")
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')

base = [
    'Flask-WTF',                 # Python flask application
    "requests",                  # Python HTTP for Humans.
    "python_jose"                # JOSE implementation in Python
]

setups = []

ir = (base)
requires = ir


def delete(path):
    if os.path.exists(path=path):
        try:
            if os.path.isfile(path=path):
                os.remove(path=path)
            else:
                shutil.rmtree(path=path)
        except:
            pass


def write_version(version, sha, filename):
    text = "__version__ = '{0}'\n__REVESION__ = '{1}'".format(version, sha)
    with open(file=filename, mode='w') as file:
        file.write(text)


def get_version(filename):
    version = "1.0.0"  # Adding default version

    # This block is for reading the version from Flask Cognito Auth distribution
    if os.path.exists(path=filename):
        contents = None
        with open(file=filename, mode="r") as file:
            contents = file.read()
            version = VERSION_RE.search(contents).group(1)
            return version

    # If file not found. Then may be local or want to get the version
    version_python_file = os.path.join(ROOT, "version.py")
    if os.path.exists(path=version_python_file):
        import version as ver
        version = ver.version

        sha = ""
        try:
            import git
            repo = git.Repo(path=".", search_parent_directories=True)
            sha = repo.head.commit.hexsha
            sha = repo.git.rev_parse(sha, short=6)
        except ImportError:
            print(f"Import error on git, can be ignored for build")
            pass
        except Exception as exception:
            print(str(exception))
            traceback.print_tb(exception.__traceback__)
            pass
        write_version(version=version, sha=sha, filename=filename)
    return version


def replace_string_in_file(old_string, new_string, input, output=None):
    # Safely read the input filename using 'with'
    with open(file=input, mode="r") as f:
        newText = f.read().replace(old_string, new_string)

    if not output or not len(output):
        output = input

    # Safely write the changed content, if found in the file
    with open(file=output, mode="w") as f:
        f.write(newText)


with open("README.md", "r") as f:
    long_description = f.read()


def do_setup():
    setup(
        name=__NAME__,
        version=get_version(filename=VERSION_FILE),
        description='Flask Cognito Authentication',
        long_description=long_description,
        long_description_content_type="text/markdown",
        keywords=['flask', 'amazon cognito', 'json web token',
                  'authentication', 'autorization'],
        author='Ankit Shrivastava',
        url='https://github.com/ankit-shrivastava/flask-cognito-auth',
        packages=find_packages(include=[__NAME__.replace("-", "_")]),
        include_package_data=True,
        setup_requires=setups,
        install_requires=requires,
        license="MIT",
        python_requires='>=3.4',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Web Environment',
            'Framework :: Flask',
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Software Development :: Version Control :: Git',
        ],
    )


if __name__ == '__main__':
    import sys
    do_setup()
    if "sdist" in sys.argv or "bdist_wheel" in sys.argv:
        egg_info = os.path.join(ROOT, __NAME__.replace("-", "_") + '.egg-info')
        delete(path=egg_info)
        eggs = os.path.join(ROOT, '.eggs')
        delete(path=eggs)
        delete(path=VERSION_FILE)
        egg_info = os.path.join(ROOT, "build")
        delete(path=egg_info)
