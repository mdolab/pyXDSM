.. pyXDSM documentation master file, created by
   sphinx-quickstart on Fri Oct 16 11:16:12 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _pyXDSM:

======
pyXDSM
======

Introduction
============

``pyXDSM`` is a python library to generate XDSM diagrams in high-quality pdf format.

What is XDSM?
-------------

The eXtended Design Structure Matrix (XDSM) is a graphical language for describing the movement of data and the execution sequence for a multidisciplinary optimization problem. 
You can read the `paper by Lambe and Martins <http://mdolab.engin.umich.edu/bibliography/Lambe2012a.html>`_ for all the details.

How to use it
=============

The following pages provide detailed info on how to use the python library:

.. toctree::
   :caption: User guide
   :maxdepth: 1

   install
   examples
   API

TikZ and LaTeX
--------------
You need to install these libraries for pyXDSM to work. See the `install guide <https://www.latex-project.org/get/>`_ for your platform.

Embedding the diagram directly in LaTeX
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition, the file, ``mdf.tikz``, can be embedded in another `.tex` file using
the ``\input`` command:

.. code-block:: latex

   \begin{figure}
   \caption{Example of an MDF XDSM.}
   \centering
   \input{mdf.tikz}
   \label{fig:xdsm}
   \end{figure}


The following is required to be in the preamble of the document:

.. code-block:: latex

   \usepackage{geometry}
   \usepackage{amsfonts}
   \usepackage{amsmath}
   \usepackage{amssymb}
   \usepackage{tikz}

   \usetikzlibrary{arrows,chains,positioning,scopes,shapes.geometric,shapes.misc,shadows}

