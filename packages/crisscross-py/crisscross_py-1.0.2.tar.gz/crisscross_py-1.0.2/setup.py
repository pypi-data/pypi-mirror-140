# -*-Mode:python;coding:utf-8;tab-width:4;c-basic-offset:4;indent-tabs-mode:()-*-
# ex: set ft=python fenc=utf-8 sts=4 ts=4 sw=4 et:

try:
    from setuptools import setup, Command
except ImportError:
    from distutils.core import setup, Command


long_description = open("README.md", "r").read()
setup(
    install_requires=["elixir_py", "redis", "base58"],
    name="crisscross_py",
    py_modules=["crisscross"],
    scripts=["./scripts/crisscross"],
    license="MIT",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Erlang",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
    ],
    version="1.0.2",
    description="Python Client for CrissCross Network",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kyle Hanson",
    author_email="kyle@statetrace.com",
    url="https://github.com/SoCal-Software-Labs/crisscross_py",
)
