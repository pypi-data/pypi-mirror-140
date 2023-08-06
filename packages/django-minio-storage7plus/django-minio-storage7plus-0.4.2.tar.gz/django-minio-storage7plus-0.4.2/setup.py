# encoding: utf-8
from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name="django-minio-storage7plus",
    version="0.4.2",
    license="MIT",
    description="Django file storage using the minio python client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Philipp Lutzke",
    author_email="philipp@funkhaus.io",
    packages=[
        "minio_storage",
        "minio_storage/management/",
        "minio_storage/management/commands/",
    ],
    setup_requires=["setuptools_scm"],
    install_requires=["django>=1.11", "minio>=7,<8"],
    extras_require={"test": ["coverage", "requests"]},
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Framework :: Django",
    ],
)
