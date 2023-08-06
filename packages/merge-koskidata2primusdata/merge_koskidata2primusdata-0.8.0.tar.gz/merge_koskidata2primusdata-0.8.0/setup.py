import io
import os
import re

from setuptools import find_packages
from setuptools import setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, mode="r", encoding="utf-8") as fd:
        return re.sub(text_type(r":[a-z]+:`~?(.*?)`"), text_type(r"``\1``"), fd.read())


setup(
    name="merge_koskidata2primusdata",
    packages=["merge_koskidata2primusdata"],
    entry_points={
        "console_scripts": [
            "merge_student_years=merge_koskidata2primusdata.merge_student_years:main",
            "add_column=merge_koskidata2primusdata.add_column:main",
        ]
    },
    version="0.8.0",
    url="https://github.com/pasiol/merge_koskidata2primusdata.git",
    license="GNU Lesser General Public License v3.0 or later (LGPLv3.0+)",
    author="Pasi Ollikainen",
    author_email="pasi.ollikainen@outlook.com",
    description="Utility which merging Koski and Primus CSV reports.",
    long_description=read("README.rst"),
    install_requires=[
        "pandas>=1.0.1",
        "numpy>=1.18.1",
        "Click>=7.0",
        "openpyxl>=3.0.3",
        "xlrd>=1.2.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
    ],
)
