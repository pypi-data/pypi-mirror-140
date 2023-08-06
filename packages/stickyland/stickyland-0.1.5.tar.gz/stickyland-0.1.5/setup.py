"""
jupyterlab_stickyland setup
"""
import json
import sys
from pathlib import Path

import setuptools

# The name of the project
name = "stickyland"

labext_name = "jupyterlab-stickyland"

with open('./README.md') as fp:
    long_description = fp.read()

setup_args = dict(
    name=name,
    version="0.1.5",
    url="https://github.com/xiaohk/stickyland",
    author="Jay Wang",
    author_email="jay@zijie.wang",
    license="BSD-3-Clause",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=["jupyterlab_stickyland"],
    zip_safe=False,
    include_package_data=True,
    python_requires=">=3.6",
    platforms="Linux, Mac OS X, Windows",
    keywords=["Jupyter", "JupyterLab", "JupyterLab3"],
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Framework :: Jupyter",
        "Framework :: Jupyter :: JupyterLab",
        "Framework :: Jupyter :: JupyterLab :: 3",
        "Framework :: Jupyter :: JupyterLab :: Extensions",
        "Framework :: Jupyter :: JupyterLab :: Extensions :: Prebuilt",
    ],
)

if __name__ == "__main__":
    setuptools.setup(**setup_args)
