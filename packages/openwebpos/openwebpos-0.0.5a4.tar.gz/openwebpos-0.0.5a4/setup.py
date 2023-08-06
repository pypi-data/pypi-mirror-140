import os

from setuptools import setup, find_packages

VERSION = '0.0.5a4'
DESCRIPTION = 'Web-based point of sale system.'

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="openwebpos",
    version=VERSION,
    url="https://github.com/baezfb/openwebpos",
    author="Javier Baez",
    author_email="baezdevs@gmail.com",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    install_requires=[
        "flask ~= 2.0"
    ],
    keywords=['python', 'pos', 'point-of-sale'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Framework :: Flask",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    extras_require={
        "dev": [

        ]
    },
)

try:
    os.mkdir('instance')
except FileExistsError:
    pass

try:
    with open("instance/__init__.py", "x") as f:
        f.write('Create __init__.py file')
    with open("instance/settings.py", "x") as sf:
        sf.write('Create settings.py file')
except FileNotFoundError:
    print("The 'instance' directory does not exist")
except FileExistsError:
    pass
