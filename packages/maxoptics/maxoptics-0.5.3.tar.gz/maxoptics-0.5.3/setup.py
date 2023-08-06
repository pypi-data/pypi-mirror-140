# -*-coding:utf-8 -*-
from setuptools import setup, find_packages

from maxoptics import __VERSION__

setup(
    name="maxoptics",
    version=__VERSION__,
    author="MaxOptics",
    author_email="rao-jin@maxoptics.com",
    description="MaxOptics SDK",
    # long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages() + ["maxoptics/autogen", "maxoptics/static_modules"],
    platforms="Independent",
    python_requires=">=3.8.5",
    package_data={"maxoptics": ["autogen/*", "static_modules/*", "default.conf"]},
    include_package_data=True,
    install_requires=[
        "requests",
        "matplotlib",
        "numpy",
        "pandas",
        "seaborn",
        "pyyaml",
        "gdspy",
        "python-socketio",
    ],
    url="",
    zip_safe=False,
    classfiers=[
        "Development Status :: 3 -Alpha",
        "Intended Audience :: Maxoptics Developers",
        "Topic :: Software Development Kit :: Build Tools",
        "License",
        "Programming Language :: Python :: 3.8",
    ],
)
