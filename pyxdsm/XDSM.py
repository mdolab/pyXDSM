from __future__ import print_function
import os
import numpy as np
import json

from collections import namedtuple

from pyxdsm import __version__ as pyxdsm_version

tikzpicture_template = r"""
%%% Preamble Requirements %%%
% \usepackage{{geometry}}
% \usepackage{{amsfonts}}
% \usepackage{{amsmath}}
% \usepackage{{amssymb}}
% \usepackage{{tikz}}

% Optional packages such as sfmath set through python interface
% \usepackage{{{optional_packages}}}

% \usetikzlibrary{{arrows,chains,positioning,scopes,shapes.geometric,shapes.misc,shadows}}

%%% End Preamble Requirements %%%

\input{{"{diagram_styles_path}"}}
\begin{{tikzpicture}}

\matrix[MatrixSetup]{{
{nodes}}};

% XDSM process chains
{process}

\begin{{pgfonlayer}}{{data}}
\path
{edges}
\end{{pgfonlayer}}

\end{{tikzpicture}}
"""

tex_template = r"""
% XDSM diagram created with pyXDSM {version}.
\documentclass{{article}}
\usepackage{{geometry}}
\usepackage{{amsfonts}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{tikz}}

% Optional packages such as sfmath set through python interface
\usepackage{{{optional_packages}}}

% Define the set of TikZ packages to be included in the architecture diagram document
\usetikzlibrary{{arrows,chains,positioning,scopes,shapes.geometric,shapes.misc,shadows}}


% Set the border around all of the architecture diagrams to be tight to the diagrams themselves
% (i.e. no longer need to tinker with page size parameters)
\usepackage[active,tightpage]{{preview}}
\PreviewEnvironment{{tikzpicture}}
\setlength{{\PreviewBorder}}{{5pt}}

\begin{{document}}

\input{{"{tikzpicture_path}"}}

\end{{document}}
"""

def chunk_label(label, n_chunks): 
    # looping till length l 
    for i in range(0, len(label), n_chunks):  
        yield label[i:i + n_chunks] 

def _parse_label(label, label_width=None):
    if isinstance(label, (tuple, list)):
        if label_width is None: 
            return r'$\begin{array}{c}' + r' \\ '.join(label) + r'\end{array}$'
        else: 
            labels = []
            for chunk in chunk_label(label, label_width): 
                labels.append(", ".join(chunk))
            return r'$\begin{array}{c}' + r' \\ '.join(labels) + r'\end{array}$'
    else:
        return r'${}$'.format(label)

def _label_to_spec(label, spec): 
    if isinstance(label, str): 
        label = [label,]
    for var in label: 
        spec.add(var)


System = namedtuple('System', 'node_name style label stack faded text_width spec_name')
Input = namedtuple('Input', 'node_name label label_width style stack')
Output = namedtuple('Output', 'node_name label label_width style stack side')
Connection = namedtuple('Connection', 'src target label label_width style stack faded')

class XDSM(object):

    def __init__(self, use_sfmath=True):
        self.systems = []
        self.connections = []
        self.left_outs = {}
        self.right_outs = {}
        self.ins = {}
        self.processes = []
        self.process_arrows = []

        self.use_sfmath=use_sfmath

       
    def add_system(self, node_name, style, label, stack=False, faded=False, text_width=None, spec_name=None):
        if spec_name is None: 
            spec_name = node_name

        sys = System(node_name, style, label, stack, faded, text_width, spec_name)
        self.systems.append(sys)

    def add_input(self, name, label, label_width=4, style='DataIO', stack=False):
        self.ins[name] = Input('output_'+name, label, label_width, style, stack)


    def add_output(self, name, label, label_width=4, style='DataIO', stack=False, side="left"):
        if side == "left":
            self.left_outs[name] = Output('left_output_'+name, label, label_width, style, stack, side)
        elif side == "right":
            self.right_outs[name] = Output('right_output_'+name, label, label_width, style, stack, side)

    def connect(self, src, target, label, label_width=4, style='DataInter', stack=False, faded=False):
        if src == target:
            raise ValueError('Can not connect component to itself')
        self.connections.append(Connection(src, target, label, label_width, style, stack, faded))

    def add_process(self, systems, arrow=True):
        self.processes.append(systems)
        self.process_arrows.append(arrow)
    
    def _build_node_grid(self):
        size = len(self.systems)

        comps_rows = np.arange(size)
        comps_cols = np.arange(size)

        if self.ins:
            size += 1
            # move all comps down one row
            comps_rows += 1

        if self.left_outs:
            size += 1
            # shift all comps to the right by one, to make room for inputs
            comps_cols += 1

        if self.right_outs:
            size += 1
            # don't need to shift anything in this case

        # build a map between comp node_names and row idx for ordering calculations
        row_idx_map = {}
        col_idx_map = {}

        node_str = r'\node [{style}] ({node_name}) {{{node_label}}};'

        grid = np.empty((size, size), dtype=object)
        grid[:] = ''

        # add all the components on the diagonal
        for i_row, j_col, comp in zip(comps_rows, comps_cols, self.systems):
            style = comp.style
            if comp.stack is True:  # stacking
                style += ',stack'
            if comp.faded is True:  # fading
                style += ',faded'
            if comp.text_width is not None:
                style += ',text width={}cm'.format(comp.text_width)

            label = _parse_label(comp.label)
            node = node_str.format(style=comp.style, node_name=comp.node_name, node_label=label)
            grid[i_row, j_col] = node

            row_idx_map[comp.node_name] = i_row
            col_idx_map[comp.node_name] = j_col

        # add all the off diagonal nodes from components
        for conn in self.connections:
            # src, target, style, label, stack, faded, label_width
            src_row = row_idx_map[conn.src]
            target_col = col_idx_map[conn.target]

            loc = (src_row, target_col)

            style = conn.style
            if conn.stack is True:  # stacking
                style += ',stack'
            if conn.faded is True:  # fading
                style += ',faded'

            label = _parse_label(conn.label, conn.label_width)

            node_name = '{}-{}'.format(conn.src, conn.target)

            node = node_str.format(style=style,
                                   node_name=node_name,
                                   node_label=label)

            grid[loc] = node

        # add the nodes for left outputs
        for comp_name, out in self.left_outs.items():
            style = out.style
            if out.stack:
                style += ',stack'

            i_row = row_idx_map[comp_name]
            loc = (i_row, 0)

            label = _parse_label(out.label, out.label_width)
            node = node_str.format(style=style,
                                   node_name=out.node_name,
                                   node_label=label)

            grid[loc] = node

        # add the nodes for right outputs
        for comp_name, out in self.right_outs.items():
            style = out.style
            if out.stack:
                style += ',stack'

            i_row = row_idx_map[comp_name]
            loc = (i_row, -1)
            label = _parse_label(out.label, out.label_width)
            node = node_str.format(style=style,
                                   node_name=out.node_name,
                                   node_label=label)

            grid[loc] = node

        # add the inputs to the top of the grid
        for comp_name, inp in self.ins.items():
            # node_name, style, label, stack = in_data
            style = inp.style
            if inp.stack:
                style += ',stack'

            j_col = col_idx_map[comp_name]
            loc = (0, j_col)
            label = _parse_label(inp.label, label_width=inp.label_width)
            node = node_str.format(style=style,
                                   node_name=inp.node_name,
                                   node_label=label)

            grid[loc] = node

        # mash the grid data into a string
        rows_str = ''
        for i, row in enumerate(grid):
            rows_str += "%Row {}\n".format(i) + '&\n'.join(row) + r'\\'+'\n'

        return rows_str

    def _build_edges(self):
        h_edges = []
        v_edges = []

        edge_string = "({start}) edge [DataLine] ({end})"
        for conn in self.connections:
            od_node_name = '{}-{}'.format(conn.src, conn.target)
            h_edges.append(edge_string.format(start=conn.src, end=od_node_name))
            v_edges.append(edge_string.format(start=od_node_name, end=conn.target))

        for comp_name, out in self.left_outs.items():
            node_name = out.node_name
            h_edges.append(edge_string.format(start=comp_name, end=node_name))

        for comp_name, out in self.right_outs.items():
            node_name = out.node_name
            h_edges.append(edge_string.format(start=comp_name, end=node_name))

        for comp_name, inp in self.ins.items():
            node_name = inp.node_name
            v_edges.append(edge_string.format(start=comp_name, end=node_name))

        paths_str = '% Horizontal edges\n' + '\n'.join(h_edges) + '\n'
        paths_str += '% Vertical edges\n' + '\n'.join(v_edges) + ';'

        return paths_str

    def _build_process_chain(self):
        sys_names = [s.node_name for s in self.systems]
        output_names = [data[0] for _, data in self.ins.items()] + [data[0] for _, data in self.left_outs.items()] + [data[0] for _, data in self.right_outs.items()]
        # comp_name, in_data in self.ins.items():
        #     node_name, style, label, stack = in_data
        chain_str = ""

        for proc, arrow in zip(self.processes, self.process_arrows):
            chain_str += "{ [start chain=process]\n \\begin{pgfonlayer}{process} \n"
            start_tip = False
            for i, sys in enumerate(proc):
                if sys not in sys_names and sys not in output_names:
                    raise ValueError('process includes a system named "{}" but no system with that name exists.'.format(sys))
                if sys in output_names and i == 0:
                    start_tip = True
                if i == 0:
                    chain_str += "\\chainin ({});\n".format(sys)
                else:
                    if sys in output_names or (i == 1 and start_tip):
                        if arrow:
                            chain_str += "\\chainin ({}) [join=by ProcessTipA];\n".format(sys)
                        else:
                            chain_str += "\\chainin ({}) [join=by ProcessTip];\n".format(sys)
                    else:
                        if arrow:
                            chain_str += "\\chainin ({}) [join=by ProcessHVA];\n".format(sys)
                        else:
                            chain_str += "\\chainin ({}) [join=by ProcessHV];\n".format(sys)
            chain_str += "\\end{pgfonlayer}\n}"

        return chain_str

    def _compose_optional_package_list(self):

        # Check for optional LaTeX packages
        optional_packages_list = []
        if self.use_sfmath:
            optional_packages_list.append('sfmath')

        # Join all packages into one string separated by comma
        optional_packages_str = ",".join(optional_packages_list)

        return optional_packages_str

    def write(self, file_name, build=True, cleanup=True, quiet=False):
        """
        Write output files for the XDSM diagram.  This produces the following:

            - {file_name}.tikz
                A file containing the TikZ definition of the XDSM diagram.
            - {file_name}.tex
                A standalone document wrapped around an include of the TikZ file which can
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
            Flag that determines if pdflatex build files will be deleted after build is complete
        quiet: bool
            Set to True to suppress output from pdflatex.
        """
        nodes = self._build_node_grid()
        edges = self._build_edges()
        process = self._build_process_chain()

        module_path = os.path.dirname(__file__)
        diagram_styles_path = os.path.join(module_path, 'diagram_styles')
        # Hack for Windows. MiKTeX needs Linux style paths.
        diagram_styles_path = diagram_styles_path.replace('\\', '/')

        optional_packages_str = self._compose_optional_package_list()

        tikzpicture_str = tikzpicture_template.format(nodes=nodes,
                                                      edges=edges,
                                                      process=process,
                                                      diagram_styles_path=diagram_styles_path,
                                                      optional_packages=optional_packages_str)

        with open(file_name + '.tikz', 'w') as f:
            f.write(tikzpicture_str)

        tex_str = tex_template.format(nodes=nodes, edges=edges,
                                      tikzpicture_path=file_name + '.tikz',
                                      diagram_styles_path=diagram_styles_path,
                                      optional_packages=optional_packages_str,
                                      version=pyxdsm_version)

        if file_name:
            with open(file_name + '.tex', 'w') as f:
                f.write(tex_str)

        if build:
            command = 'pdflatex '
            if quiet:
                command += " -interaction=batchmode -halt-on-error "
            os.system(command + file_name + '.tex')
            if cleanup:
                for ext in ['aux', 'fdb_latexmk', 'fls', 'log']:
                    f_name = '{}.{}'.format(file_name, ext)
                    if os.path.exists(f_name):
                        os.remove(f_name)


    def write_sys_specs(self, folder_name): 
        """
        Write i/o spec files for components to specified folder

        Parameters
        ----------
        folder_name: str
            name of the folder, which will be created if it doesn't exist, to put spec files into
        """

        # find un-connected to each system by looking at Inputs
        specs = {}
        for sys in self.systems: 
            specs[sys.node_name] = {'inputs': set(), 'outputs': set()}

        for sys_name, inp in self.ins.items():
            _label_to_spec(inp.label, specs[sys_name]['inputs'])

        # find connected inputs/outputs to each system by looking at Connections
        for conn in self.connections: 
            _label_to_spec(conn.label, specs[conn.target]['inputs'])
            
            _label_to_spec(conn.label, specs[conn.src]['outputs'])

        # find unconnected outputs to each system by looking at Outputs
        for sys_name, out in self.left_outs.items():
            _label_to_spec(out.label, specs[sys_name]['outputs']) 
        for sys_name, out in self.right_outs.items():
            _label_to_spec(out.label, specs[sys_name]['outputs']) 

        if not os.path.isdir(folder_name): 
            os.mkdir(folder_name)

        for sys in self.systems: 
            if sys.spec_name is not False: 
                path = os.path.join(folder_name, sys.spec_name + ".json")
                with open(path, 'w') as f: 
                    spec = specs[sys.node_name]
                    spec['inputs'] = list(spec['inputs'])
                    spec['outputs'] = list(spec['outputs'])
                    json_str = json.dumps(spec, indent=2)
                    f.write(json_str)
