import re
from setuptools import find_packages, setup


def get_info(pyfile):
    info = {}
    info_re = re.compile(r"__(\w+)__ = '(.*)'")
    with open(pyfile, 'r') as f:
        for line in f.readlines():
            match = info_re.search(line)
            if match:
                info[match.group(1)] = match.group(2)

    return info

info = get_info('cpenv/__init__.py')


with open("README.rst") as f:
    readme = f.read()


setup(
    name=info['title'],
    version=info['version'],
    description=info['description'],
    long_description=readme,
    author=info['author'],
    author_email=info['email'],
    url=info['url'],
    license=info['license'],
    packages=find_packages(),
    package_data={
        'cpenv': ['bin/*.*']
    },
    include_package_data=True,
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ),
    entry_points={
        'console_scripts': ['cpenv = cpenv.__main__:cli']
    },
    install_requires=['virtualenv']
)
