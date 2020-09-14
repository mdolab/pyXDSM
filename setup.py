from setuptools import setup
import re
from os import path

__version__ = re.findall(
    r"""__version__ = ["']+([0-9\.]*)["']+""",
    open("pyxdsm/__init__.py").read(),
)[0]

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pyXDSM",
    version=__version__,
    description="Python script to generate PDF XDSM diagrams using TikZ and LaTeX",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="optimization multidisciplinary multi-disciplinary analysis n2 xdsm",
    author="",
    author_email="",
    url="https://github.com/mdolab/pyXDSM",
    license="Apache License Version 2.0",
    packages=[
        "pyxdsm",
    ],
    package_data={"pyxdsm": ["*.tex"]},
    install_requires=["numpy>=1.16"],
    python_requires=">=3",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
