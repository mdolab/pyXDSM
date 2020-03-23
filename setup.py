from setuptools import setup
import re

__version__ = re.findall(
    r"""__version__ = ["']+([0-9\.]*)["']+""",
    open('pyxdsm/__init__.py').read(),
)[0]

setup(name='pyXDSM',
      version=__version__,
      description="Python script to generate PDF XDSM diagrams using TikZ and LaTeX",
      long_description="""A python library for generating publication quality PDF XDSM diagrams.
    This library is a thin wrapper that uses the TikZ library and LaTeX to build the PDFs.

     ## What is XDSM?
    The eXtended Design Struture Matrix (XDSM) is a graphical language for describing the movement of data and  the execution sequence for a  multidisciplinary optimization  problem.
    You can read the [paper by Lambe and Martins](http://mdolab.engin.umich.edu/content/extensions-design-structure-matrix) for all the details.
    If you  would like a citation for XDSM, here is the bibtex for that paper:

    @article {Lambe2012,  
        title = {Extensions to the Design Structure Matrix for the Description of Multidisciplinary Design, Analysis, and Optimization Processes},   
        journal = {Structural and Multidisciplinary Optimization},  
        volume = {46},  
        year = {2012},  
        pages = {273-284},  
        doi = {10.1007/s00158-012-0763-y},  
        author = {Andrew B. Lambe and Joaquim R. R. A. Martins}
    }

      """,
    long_description_content_type="text/markdown",
      keywords='optimization multidisciplinary multi-disciplinary analysis n2 xdsm',
      author='',
      author_email='',
      url='https://github.com/mdolab/pyXDSM',
      license='Apache License Version 2.0',
      packages=[
          'pyxdsm',
      ],
      package_data={
          'pyxdsm': ['*.tex']
      },
      install_requires=[
            'numpy>=1.9.2'
      ],
      classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python"]
      )

