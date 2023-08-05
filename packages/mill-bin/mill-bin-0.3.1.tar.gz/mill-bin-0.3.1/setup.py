# coding:utf-8

from setuptools import setup

setup(
    name="mill-bin",
    url='https://github.com/jlsemi',
    packages=["mill_bin"],
    package_data={
        "mill_bin": [
            "assets/mill",
        ],
    },
    use_scm_version={"relative_to": __file__, "write_to": "mill_bin/version.py",},
    author="Leway Colin@JLSemi",
    author_email="colinlin@jlsemi.com",
    description=(
        "Mill Binary is a fat JAR with all of its dependencies."
    ),
    license="Apache-2.0 License",
    keywords=[
        "mill",
    ],
    entry_points={"console_scripts": ["mill_bin = mill_bin.main:main"]},
    setup_requires=["setuptools_scm",],
    install_requires=[
    ],
    # Supported Python versions: 3.6+
    python_requires=">=3.6",
)
