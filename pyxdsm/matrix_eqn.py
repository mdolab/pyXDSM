from __future__ import division

import os

import numpy as np

from collections import namedtuple


# color pallette link: http://paletton.com/#uid=72Q1j0kllllkS5tKC9H96KClOKC

base_file_start = r"""\documentclass[border=0pt]{standalone}
% Justin S. Gray 2018
% Based off code by John T. Hwang (2014), who based his code off Alec Jacobson: http://www.alecjacobson.com/weblog/?p=1289

% nc = necessary comment [do not remove]

% Four rules for using these macros:
% 1. Always start with a row
% 2. Rows contain cols and cols contain rows
% 3. Mats should be on at least the 3rd level (row->col->mat, minimum)
% 4. If a row contains the mat, add &; if a col contains the mat, add \\

% ---------------------------------------

\usepackage{tikz}
\usepackage{ifthen}
\usepackage{esdiff}
\usepackage{varwidth}

\definecolor{tableau0}{RGB}{77, 121, 168}
\definecolor{tableau1}{RGB}{242, 142, 43}
\definecolor{tableau2}{RGB}{255, 87, 88}
\definecolor{tableau3}{RGB}{118, 183, 178}
\definecolor{tableau4}{RGB}{89, 161, 78}
\definecolor{tableau5}{RGB}{237, 201, 72}
\definecolor{tableau6}{RGB}{176, 121, 162}
\definecolor{tableau7}{RGB}{255, 157, 167}
\definecolor{tableau8}{RGB}{156, 116, 94}
\definecolor{tableau9}{RGB}{186, 176, 172}


\newcommand{\thk}{0.01in}
\newcommand{\thkln}{0.02in}

% \blockmat{width}{height}{text}{block_options}{other}
\newcommand{\blockmat}[5]{
\begin{tikzpicture}
    \draw[draw=white,fill=white,#4,line width=\thk] (0,0) rectangle( #1-\thk,#2-\thk);
    #5
    \draw (#1/2, #2/2) node {#3};
\end{tikzpicture}
}

% blockempty{width}{height}{text}
\newcommand{\blockempty}[3]{
    \blockmat{#1}{#2}{#3}{draw=white,fill=white}{}%
}

% \blockmat{width}{height}{text}{block_options}{diagonal_width}{diagonal_options}
\newcommand{\blockdiag}[6]{
    \blockmat{#1}{#2}{#3}{#4}
    {
    \draw[#6,line width=\thk] (0,#2-\thk) -- (#5,#2-\thk) -- ( #1-\thk,#5) -- ( #1-\thk,0) -- ( #1-\thk - #5,0) -- (0,#2-\thk -#5) --cycle;
    }%
}

% \blockddots{width}{height}{text}{block_options}{dot_radius}{dot_options}{dot_h}{dot_v}
\newcommand{\blockdots}[8]{
    \blockmat{#1}{#2}{#3}{#4}%
    {%
    \ifthenelse{\equal{#5}{}}
    {\newcommand\dotradius{0.01in}}
    {\newcommand\dotradius{#5}}%
    \filldraw[#6] (#1/2, #2/2) circle (0.5*\dotradius);%
    \filldraw[#6] (#1/2 + #7, #2/2 + #8) circle (0.5*\dotradius);%
    \filldraw[#6] (#1/2 - #7, #2/2 - #8) circle (0.5*\dotradius);%
    }%
}

% \leftbracket{width}{height}{options}
\newcommand{\leftbracket}[3]{
    \begin{tikzpicture}
        \coordinate (iSW) at (\thk+\thkln/2,\thk+\thkln/2);
        \coordinate (iNW) at (\thk+\thkln/2,#2-\thk-\thkln/2);
        \coordinate (iSE) at (#1-\thk-\thkln/2,\thk+\thkln/2);
        \coordinate (iNE) at (#1-\thk-\thkln/2,#2-\thk-\thkln/2);
        \coordinate (oSW) at (\thk/2,\thk/2);
        \coordinate (oNW) at (\thk/2,#2-\thk/2);
        \coordinate (oSE) at (#1-\thk/2,\thk/2);
        \coordinate (oNE) at (#1-\thk/2,#2-\thk/2);
        \draw[#3,line width=\thkln] (iNE) -- (iNW) -- (iSW) -- (iSE);
        \draw[draw=white,line width=\thk] (oNE) -- (oNW) -- (oSW) -- (oSE);
    \end{tikzpicture}%nc
}

% \rightbracket{width}{height}{options}
\newcommand{\rightbracket}[3]{
    \begin{tikzpicture}
        \coordinate (iSW) at (\thk+\thkln/2,\thk+\thkln/2);
        \coordinate (iNW) at (\thk+\thkln/2,#2-\thk-\thkln/2);
        \coordinate (iSE) at (#1-\thk-\thkln/2,\thk+\thkln/2);
        \coordinate (iNE) at (#1-\thk-\thkln/2,#2-\thk-\thkln/2);
        \coordinate (oSW) at (\thk/2,\thk/2);
        \coordinate (oNW) at (\thk/2,#2-\thk/2);
        \coordinate (oSE) at (#1-\thk/2,\thk/2);
        \coordinate (oNE) at (#1-\thk/2,#2-\thk/2);
        \draw[#3,line width=\thkln] (iNW) -- (iNE) -- (iSE) -- (iSW);
        \draw[draw=white,line width=\thk] (oNW) -- (oNE) -- (oSE) -- (oSW);
    \end{tikzpicture}%nc
}

% \upperbracket{width}{height}{options}
\newcommand{\upperbracket}[3]{
    \begin{tikzpicture}
        \coordinate (iSW) at (\thk+\thkln/2,\thk+\thkln/2);
        \coordinate (iNW) at (\thk+\thkln/2,#2-\thk-\thkln/2);
        \coordinate (iSE) at (#1-\thk-\thkln/2,\thk+\thkln/2);
        \coordinate (iNE) at (#1-\thk-\thkln/2,#2-\thk-\thkln/2);
        \coordinate (oSW) at (\thk/2,\thk/2);
        \coordinate (oNW) at (\thk/2,#2-\thk/2);
        \coordinate (oSE) at (#1-\thk/2,\thk/2);
        \coordinate (oNE) at (#1-\thk/2,#2-\thk/2);
        \draw[#3,line width=\thkln] (iSW) -- (iNW) -- (iNE) -- (iSE);
        \draw[draw=white,line width=\thk] (oSW) -- (oNW) -- (oNE) -- (oSE);
    \end{tikzpicture}%nc
}

% \lowerbracket{width}{height}{options}
\newcommand{\lowerbracket}[3]{
    \begin{tikzpicture}
        \coordinate (iSW) at (\thk+\thkln/2,\thk+\thkln/2);
        \coordinate (iNW) at (\thk+\thkln/2,#2-\thk-\thkln/2);
        \coordinate (iSE) at (#1-\thk-\thkln/2,\thk+\thkln/2);
        \coordinate (iNE) at (#1-\thk-\thkln/2,#2-\thk-\thkln/2);
        \coordinate (oSW) at (\thk/2,\thk/2);
        \coordinate (oNW) at (\thk/2,#2-\thk/2);
        \coordinate (oSE) at (#1-\thk/2,\thk/2);
        \coordinate (oNE) at (#1-\thk/2,#2-\thk/2);
        \draw[#3,line width=\thkln] (iNW) -- (iSW) -- (iSE) -- (iNE);
        \draw[draw=white,line width=\thk] (oNW) -- (oSW) -- (oSE) -- (oNE);
    \end{tikzpicture}%nc
}

% a hack so that I don't have to worry about the number of columns or
% spaces between columns in the tabular environment
\newenvironment{blockmatrixtabular}
{%nc
    \renewcommand{\arraystretch}{0}%nc
    \begin{tabular}{
    @{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l
    @{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l
    @{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l@{}l
    @{}
    }%nc
}
{
    \end{tabular}%nc
}

% \blockcol{
% }
\newcommand{\blockcol}[1]{\vtop{\null\hbox{\begin{blockmatrixtabular}#1\end{blockmatrixtabular}}}&}

% \blockrow{
% }
\newcommand{\blockrow}[1]{\begin{blockmatrixtabular}#1\end{blockmatrixtabular}\\}


\begin{document}
\begin{varwidth}{10\textwidth}

\newcommand\mwid{0.5in}
\newcommand\wid{0.15in}
\newcommand\comp{0.3in}
\newcommand\ext{0.5in}
\newcommand\dt{0.03in}
\newcommand\txt{0.8in}

\definecolor{Tgrey}{rgb}{0.9,0.9,0.9}
\definecolor{Tred}{rgb}{1.0,0.722,0.714}
\definecolor{Tgreen}{rgb}{0.639,0.89,0.655}
\definecolor{Tblue}{rgb}{0.667,0.631,0.843}
\definecolor{Tyellow}{rgb}{1,0.941,0.714}

\definecolor{Lred}{rgb}{17.3,0.063,0.059}
\definecolor{Lgreen}{rgb}{0.047,0.133,0.051}
\definecolor{Lblue}{rgb}{0.063,0.051,0.118}
\definecolor{Lyellow}{rgb}{0.173,0.149,0.059}

\definecolor{Dgrey}{rgb}{0.4,0.4,0.4}
\definecolor{Dred}{rgb}{1.0,0.333,0.318}
\definecolor{Dgreen}{rgb}{0.282,0.89,0.322}
\definecolor{Dblue}{rgb}{0.42,0.341,0.843}
\definecolor{Dyellow}{rgb}{1.0,0.863,0.318}

\definecolor{Bred}{rgb}{0.302,0.8,0.0}
\definecolor{Bgreen}{rgb}{0.4,1.0,0.4}
\definecolor{Bblue}{rgb}{0.043,0.012,0.208}
\definecolor{Byellow}{rgb}{0.302,0.243,0.0}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
base_file_end = r"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\end{varwidth}
\end{document}"""


Variable = namedtuple('Variable', field_names=['size', 'idx', 'text', 'color'])

CellData = namedtuple('CellData', field_names=['text', 'color', 'highlight'])

def _color(base_color, h_light):
    if h_light == -1:
        color = 'white'
    elif h_light == 0:
        color = 'Tgrey'
    elif h_light == 1:
        color = 'T{}'.format(base_color)
    elif h_light == 2:
        color = 'D{}'.format(base_color)
    elif h_light == 3:
        color = 'B{}'.format(base_color)

    elif h_light == "diag":
        color = base_color

    return color

def _write_tikz(tikz, out_file, build=True, cleanup=True):
    with open('{}.tex'.format(out_file), 'w') as f:
        f.write(base_file_start)
        f.write(tikz)
        f.write(base_file_end)

    if build:
        os.system('pdflatex {}.tex'.format(out_file))

        if cleanup:
            for ext in ['aux', 'fdb_latexmk', 'fls', 'log', 'tex']:
                f_name = '{}.{}'.format(out_file, ext)
                if os.path.exists(f_name):
                    os.remove(f_name)


class TotalJacobian(object):

    def __init__(self):
        self._variables = {}
        self._j_inputs = {}
        self._n_inputs = 0

        self._i_outputs = {}
        self._n_outputs = 0

        self._connections = {}
        self._ij_connections = {}

        self._setup = False

    def add_input(self, name, size=1, text=''):
        self._variables[name] = Variable(size=size, idx=self._n_inputs, text=text, color=None)
        self._j_inputs[self._n_inputs] = self._variables[name]
        self._n_inputs += 1

    def add_output(self, name, size=1, text=''):
        self._variables[name] = Variable(size=size, idx=self._n_outputs, text=text, color=None)
        self._i_outputs[self._n_outputs] = self._variables[name]
        self._n_outputs += 1

    def connect(self, src, target, text='', color='tableau0'):
        if isinstance(target, (list, tuple)):
            for t in target:
                self._connections[src, t] = CellData(text=text, color=color, highlight='diag')
        else:
            self._connections[src, target] = CellData(text=text, color=color, highlight='diag')

    def _process_vars(self):

        if self._setup:
            return

        # deal with connections
        for (src, target), cell_data in self._connections.items():
            i_src = self._variables[src].idx
            j_target = self._variables[target].idx

            self._ij_connections[i_src, j_target] = cell_data


        self._setup = True

    def write(self, out_file=None, build=True, cleanup=True):
        """
        Write output files for the matrix equation diagram.  This produces the following:

            - {file_name}.tikz
                A file containing the TIKZ definition of the tikz diagram.
            - {file_name}.tex
                A standalone document wrapped around an include of the TIKZ file which can
                be compiled to a pdf.
            - {file_name}.pdf
                An optional compiled version of the standalone tex file.

        Parameters
        ----------
        file_name : str
            The prefix to be used for the output files
        build : bool
            Flag that determines whether the standalone PDF of the XDSM will be compiled.
            Default is True.
        cleanup: bool
            Flag that determines if padlatex build files will be deleted after build is complete
        """
        self._process_vars()

        tikz =[]

        #label the columns
        tikz.append(r'\blockrow{')
        # emtpy column for the row labels
        tikz.append(r'  \blockcol{')
        tikz.append(r'    \blockempty{%s*\comp}{%s*\comp}{%s}\\'%(1, 1, ''))
        tikz.append(r'  }')
        for j in range(self._n_inputs):
            var = self._j_inputs[j]
            col_size = var.size
            tikz.append(r'  \blockcol{')
            tikz.append(r'    \blockempty{%s*\comp}{%s*\comp}{%s}\\'%(col_size, 1, var.text))
            tikz.append(r'  }')
        tikz.append(r'}')

        for i in range(self._n_outputs):
            output = self._i_outputs[i]
            row_size = output.size

            tikz.append(r'\blockrow{')

            # label the row with the output name
            tikz.append(r'  \blockcol{')
            tikz.append(r'    \blockempty{%s*\comp}{%s*\comp}{%s}\\'%(1, row_size, output.text))
            tikz.append(r'  }')

            for j in range(self._n_inputs):
                var = self._j_inputs[j]
                col_size = var.size
                tikz.append(r'  \blockcol{')
                if (j,i) in self._ij_connections:
                    cell_data = self._ij_connections[(j,i)]
                    conn_color = 'T{}'.format(var.color)
                    if cell_data.color is not None:
                        conn_color = _color(cell_data.color, cell_data.highlight)
                    tikz.append(r'    \blockmat{%s*\comp}{%s*\comp}{%s}{draw=white,fill=%s}{}\\'%(col_size, row_size, cell_data.text, conn_color))
                else:
                    tikz.append(r'    \blockempty{%s*\comp}{%s*\comp}{}\\'%(col_size, row_size))
                tikz.append(r'  }')

            tikz.append(r'}')

        jac_tikz = "\n".join(tikz)

        _write_tikz(jac_tikz, out_file, build, cleanup)

class MatrixEquation(object):

    def __init__(self):
        self._variables = {}
        self._ij_variables = {}

        self._n_vars = 0

        self._connections = {}
        self._ij_connections = {}

        self._text = {}
        self._ij_text = {}

        self._total_size = 0

        self._setup = False

        self._terms = []

    def clear_terms(self):
        self._terms = []

    def add_variable(self, name, size=1, text='', color='blue'):
        self._variables[name] = Variable(size=size, idx=self._n_vars, text=text, color=color)
        self._ij_variables[self._n_vars] = self._variables[name]
        self._n_vars += 1

        self._total_size += size

    def connect(self, src, target, text='', color=None, highlight=1):

        if isinstance(target, (list, tuple)):
            for t in target:
                self._connections[src, t] = CellData(text=text, color=color, highlight=highlight)
        else:
            self._connections[src, target] = CellData(text=text, color=color, highlight=highlight)

    def text(self, src, target, text):
        "don't connect the src and target, but put some text where a connection would be"
        self._text[src, target] = CellData(text=text, color=None, highlight=-1)

    def _process_vars(self):
        """map all the data onto i,j grid"""

        if self._setup:
            return

        # deal with connections
        for (src, target), cell_data in self._connections.items():
            i_src = self._variables[src].idx
            i_target = self._variables[target].idx

            self._ij_connections[i_src, i_target] = cell_data

        for (src, target), cell_data in self._text.items():
            i_src = self._variables[src].idx
            j_target = self._variables[target].idx

            self._ij_text[i_src, j_target] = cell_data

        self._setup = True


    def jacobian(self, transpose=False):

        self._process_vars()

        tikz = []

        for i in range(self._n_vars):
            tikz.append(r'\blockrow{')

            row_size = self._ij_variables[i].size
            for j in range(self._n_vars):
                var = self._ij_variables[j]
                col_size = var.size
                tikz.append(r'  \blockcol{')

                if transpose:
                    location = (i,j)
                else:
                    location = (j,i)

                if i == j:
                    tikz.append(r'    \blockmat{%s*\comp}{%s*\comp}{%s}{draw=white,fill=D%s}{}\\'%(col_size, row_size, var.text, var.color))
                elif location in self._ij_connections:
                    cell_data = self._ij_connections[location]
                    conn_color = 'T{}'.format(var.color)
                    if cell_data.color is not None:
                        conn_color = _color(cell_data.color, cell_data.highlight)
                    tikz.append(r'    \blockmat{%s*\comp}{%s*\comp}{%s}{draw=white,fill=%s}{}\\'%(col_size, row_size, cell_data.text, conn_color))
                elif location in self._ij_text:
                    cell_data = self._ij_text[location]
                    tikz.append(r'    \blockempty{%s*\comp}{%s*\comp}{%s}\\'%(col_size, row_size, cell_data.text))
                else:
                    tikz.append(r'    \blockempty{%s*\comp}{%s*\comp}{}\\'%(col_size, row_size))
                tikz.append(r'  }')

            tikz.append(r'}')


        lhs_tikz = "\n".join(tikz)

        self._terms.append(lhs_tikz)
        return lhs_tikz


    def vector(self, base_color='red', highlight=None):

        self._process_vars()

        tikz = []

        if highlight is None:
            highlight = np.ones(self._n_vars)

        for i, h_light in enumerate(highlight):

            color = _color(base_color, h_light)

            row_size = self._ij_variables[i].size

            tikz.append(r'\blockrow{\blockcol{')
            if h_light == "diag":
                tikz.append(r'  \blockdiag{1*\comp}{%s*\comp}{}{draw=white,fill=T%s}{\dt}{draw=white,fill=D%s}\\'%(row_size, color, color))
            else:
                tikz.append(r'  \blockmat{1*\comp}{%s*\comp}{}{draw=white,fill=%s}{}\\'%(row_size, color))

            tikz.append(r'}}')

        vec_tikz = "\n".join(tikz)

        self._terms.append(vec_tikz)
        return vec_tikz

    def operator(self, opperator="="):

        self._process_vars()

        tikz = []

        padding_size = (self._total_size-1)/2

        tikz.append(r'\blockrow{')
        tikz.append(r'  \blockempty{\mwid}{%s*\comp}{} \\'%(padding_size))
        tikz.append(r'  \blockmat{\mwid}{1*\comp}{\huge $%s$}{draw=white,fill=white}{}\\'%(opperator))
        tikz.append(r'  \blockempty{\mwid}{%s*\comp}{} \\'%(padding_size))
        tikz.append(r'}')

        op_tikz = "\n".join(tikz)

        self._terms.append(op_tikz)
        return op_tikz

    def spacer(self):

        self._process_vars()

        tikz = []

        for i in range(self._n_vars):
            row_size = self._ij_variables[i].size

            tikz.append(r'\blockrow{\blockcol{')
            tikz.append(r'  \blockmat{.25*\mwid}{%s*\comp}{}{draw=white,fill=white}{}\\'%(row_size))
            tikz.append(r'}}')

        spacer_tikz = "\n".join(tikz)

        self._terms.append(spacer_tikz)
        return spacer_tikz


    def write(self, out_file=None, build=True, cleanup=True):
        """
        Write output files for the matrix equation diagram.  This produces the following:

            - {file_name}.tikz
                A file containing the TIKZ definition of the tikz diagram.
            - {file_name}.tex
                A standalone document wrapped around an include of the TIKZ file which can
                be compiled to a pdf.
            - {file_name}.pdf
                An optional compiled version of the standalone tex file.

        Parameters
        ----------
        file_name : str
            The prefix to be used for the output files
        build : bool
            Flag that determines whether the standalone PDF of the XDSM will be compiled.
            Default is True.
        cleanup: bool
            Flag that determines if padlatex build files will be deleted after build is complete
        """
        tikz = []
        tikz.append(r'\blockrow{')

        for term in self._terms:
            tikz.append(r'\blockcol{')
            tikz.append(term)
            tikz.append(r'}')
        tikz.append(r'}')

        eqn_tikz = "\n".join(tikz)

        if out_file:
            # with open('{}.tex'.format(out_file), 'w') as f:
            #     f.write(base_file_start)
            #     f.write(eqn_tikz)
            #     f.write(base_file_end)

            # if build:
            #     os.system('pdflatex {}.tex'.format(out_file))

            #     if cleanup:
            #         for ext in ['aux', 'fdb_latexmk', 'fls', 'log', 'tex']:
            #             f_name = '{}.{}'.format(out_file, ext)
            #             if os.path.exists(f_name):
            #                 os.remove(f_name)
            _write_tikz(eqn_tikz, out_file, build, cleanup)

if __name__ == "__main__":
    lst = MatrixEquation()

    lst.add_variable('x', text=r'$x$')
    lst.add_variable('y', size=3, text=r'$y$')
    lst.add_variable('z')

    lst.connect('x', 'y')
    lst.connect('y', 'z')
    lst.text('z', 'x', r'$0$')

    lst.jacobian(transpose=True)
    lst.spacer()
    lst.vector(base_color='green', highlight=[3,2,'diag'])
    lst.operator('=')
    lst.vector(base_color='red')
    lst.vector(base_color='red')

    lst.write('test')


    J = TotalJacobian()
    J.add_input('a', text=r'$a$')
    J.add_input('b', text=r'$b$')
    J.add_input('c', text=r'$c$')
    J.add_input('d', text=r'$d$')
    J.add_input('e', text=r'$e$')

    J.add_output('gc', text=r'$g_c$')
    J.add_output('gd', text=r'$g_d$')
    J.add_output('ge', text=r'$g_e$')
    J.add_output('f', text=r'$f$')

    J.connect('a', ('gc', 'gd', 'ge', 'f'))
    J.connect('b', ('gc', 'gd', 'ge', 'f'))
    J.connect('c', 'gc')
    J.connect('d', 'gd')
    J.connect('e', ('ge','f'))

    J.write('J_test', cleanup=False)






