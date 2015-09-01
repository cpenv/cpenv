from setuptools import find_packages, setup


with open("README.rst") as f:
    readme = f.read()


setup(
    name='cpenv',
    version='0.1.0',
    description='Cross-platform CLI for environment management.',
    long_description=readme,
    author='Dan Bradham',
    author_email='danielbradham@gmail.com',
    url='N/A',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ),
    entry_points='''
        [console_scripts]
        pycpenv=cpenv.__main__:cli
    ''',
    scripts=(
        'bin/cpenv.bat',
        'bin/cpenv.sh',
        'bin/run_py.bat',
    ),
)
