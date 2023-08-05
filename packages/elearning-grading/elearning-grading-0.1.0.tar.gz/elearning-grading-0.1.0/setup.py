import os
from typing import List

from setuptools import find_packages, setup

_PATH_ROOT = os.path.dirname(__file__)

VERSION = "0.1.0"
# python setup.py sdist
# twine upload .\dist\elearning-grading-VERSION.tar.gz
HOMEPAGE = "https://github.com/Supermaxman/elearning-grading"
DESCRIPTION = "Python utilities to help Teaching Assistants grade assignments with eLearning"


def _load_requirements(path_dir: str, file_name: str = "requirements.txt", comment_char: str = "#") -> List[str]:
    with open(os.path.join(path_dir, file_name)) as file:
        lines = [ln.strip() for ln in file.readlines()]
    requirements = []
    for ln in lines:
        # filer all comments
        if comment_char in ln:
            ln = ln[: ln.index(comment_char)].strip()
        # skip directly installed dependencies
        if ln.startswith("http") or "@http" in ln:
            continue
        if ln:
            requirements.append(ln)
    return requirements


def _load_readme_description(path_dir: str, homepage: str) -> str:
    path_readme = os.path.join(path_dir, "README.md")
    with open(path_readme, encoding="utf-8") as f:
        text = f.read()

    github_source_url = os.path.join(homepage, "blob/master")
    # replace relative repository path to absolute link to the release
    text = text.replace("docs/images/", f"{os.path.join(github_source_url, 'docs/images/')}")

    return text


LONG_DESCRIPTION = _load_readme_description(_PATH_ROOT, homepage=HOMEPAGE)

# Setting up
setup(
    name="elearning-grading",
    version=VERSION,
    author="Maxwell Weinzierl",
    author_email="maxwellweinzierl@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(exclude=["tests*", "docs*"]),
    long_description_content_type="text/markdown",
    zip_safe=False,
    include_package_data=True,
    keywords=["grading", "elearning", "education", "teaching"],
    python_requires=">=3.6",
    setup_requires=[],
    install_requires=_load_requirements(_PATH_ROOT),
    project_urls={
        "Bug Tracker": "https://github.com/Supermaxman/elearning-grading/issues",
        "Source Code": "https://github.com/Supermaxman/elearning-grading",
    },
    license="Apache-2.0",
    download_url="https://github.com/Supermaxman/elearning-grading",
    classifiers=[
        "Environment :: Console",
        "Natural Language :: English",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Topic :: Education",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points={
        "console_scripts": [
            "elg-org=elearning_grading.organize:main",
            "elg-porg=elearning_grading.project_organize:main",
            "elg-gen=elearning_grading.generate:main",
            "elg-pmem=elearning_grading.project_members:main",
        ],
    },
)
