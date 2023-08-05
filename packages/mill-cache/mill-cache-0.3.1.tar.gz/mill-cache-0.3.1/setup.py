# coding:utf-8

from setuptools import setup

setup(
    name="mill-cache",
    url='https://github.com/jlsemi',
    packages=["mill_cache"],
    package_data={
        "mill_cache": [
            "assets/cache.tar.gz",
        ],
    },
    use_scm_version={"relative_to": __file__, "write_to": "mill_cache/version.py",},
    author="Leway Colin@JLSemi",
    author_email="colinlin@jlsemi.com",
    description=(
        "Mill Cache is a tarball with all of mill's dependencies."
    ),
    license="Apache-2.0 License",
    keywords=[
        "mill cache files",
    ],
    entry_points={"console_scripts": ["mill_cache = mill_cache.main:main"]},
    setup_requires=["setuptools_scm",],
    install_requires=[
    ],
    # Supported Python versions: 3.6+
    python_requires=">=3.6",
)
