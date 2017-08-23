from __future__ import print_function
import os
import numpy as np

tex_template = r"""
\documentclass{{article}}
\usepackage{{geometry}}
\usepackage{{amsfonts}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{tikz}}

\input{{ {diagram_border_path} }}

\begin{{document}}

\input{{ {diagram_styles_path} }}

\begin{{tikzpicture}}

\matrix[MatrixSetup]{{
{nodes}}};

\begin{{pgfonlayer}}{{data}}
\path
{edges}
\end{{pgfonlayer}}

\end{{tikzpicture}}
\end{{document}}
"""

class XDSM(object):

    def __init__(self):
        self.comps = []
        self.connections = []
        self.left_outs = {}
        self.right_outs = {}
        self.ins = {}

    def add_system(self, node_name, style, label, stack=False, faded=False):
        self.comps.append([node_name, style, label, stack, faded])

    def add_input(self, name, label, style='DataIO', stack=False):
        self.ins[name] = ('output_'+name, style, label, stack)

    def add_output(self, name, label, style='DataIO', stack=False, side="left"):
        if side == "left":
            self.left_outs[name] = ('left_output_'+name, style, label, stack)
        elif side == "right":
            self.right_outs[name] = ('right_output_'+name, style, label, stack)

    def connect(self, src, target, label, style='DataInter', stack=False, faded=False):
        if src == target:
            raise ValueError('Can not connect component to itself')
        self.connections.append([src, target, style, label, stack, faded])

    def _build_node_grid(self):
        size = len(self.comps)

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
        for i_row, j_col, comp in zip(comps_rows, comps_cols, self.comps):
            style=comp[1]
            if comp[3] == True: #stacking
                style += ',stack'
            if comp[4] == True: #stacking
                style += ',faded'

            node = node_str.format(style=style, node_name=comp[0], node_label=comp[2])
            grid[i_row, j_col] = node

            row_idx_map[comp[0]] = i_row
            col_idx_map[comp[0]] = j_col

        # add all the off diagonal nodes from components
        for src, target, style, label, stack, faded in self.connections:
            src_row = row_idx_map[src]
            target_col = col_idx_map[target]

            loc = (src_row, target_col)

            style=style
            if stack == True: #stacking
                style += ',stack'
            if faded == True:
                style += ',faded'

            node_name = '{}-{}'.format(src,target)
            node = node_str.format(style=style,
                                   node_name=node_name,
                                   node_label=label)

            grid[loc] = node

        # add the nodes for left outputs
        for comp_name, out_data in self.left_outs.items():
            node_name, style, label, stack = out_data
            if stack:
                style += ',stack'

            i_row = row_idx_map[comp_name]
            loc = (i_row,0)
            node = node_str.format(style=style,
                                   node_name=node_name,
                                   node_label=label)

            grid[loc] = node

         # add the nodes for right outputs
        for comp_name, out_data in self.right_outs.items():
            node_name, style, label, stack = out_data
            if stack:
                style += ',stack'

            i_row = row_idx_map[comp_name]
            loc = (i_row,-1)
            node = node_str.format(style=style,
                                   node_name=node_name,
                                   node_label=label)

            grid[loc] = node

        # add the inputs to the top of the grid
        for comp_name, in_data in self.ins.items():
            node_name, style, label, stack = in_data
            if stack:
                style = ',stack'

            j_col = col_idx_map[comp_name]
            loc = (0,j_col)
            node = node_str.format(style=style,
                                   node_name=node_name,
                                   node_label=label)

            grid[loc] = node

        # mash the grid data into a string
        rows_str = ''
        for i, row in enumerate(grid):
            rows_str += "%Row {}\n".format(i) +'&\n'.join(row) + r'\\'+'\n'

        return rows_str

    def _build_edges(self):
        h_edges = []
        v_edges = []

        edge_string = "({start}) edge [DataLine] ({end})"
        for src, target, style, label, stack, faded in self.connections:
            od_node_name = '{}-{}'.format(src,target)
            h_edges.append(edge_string.format(start=src, end=od_node_name))
            v_edges.append(edge_string.format(start=od_node_name, end=target))

        for comp_name, out_data in self.left_outs.items():
            node_name, style, label, stack = out_data
            h_edges.append(edge_string.format(start=comp_name, end=node_name))

        for comp_name, out_data in self.right_outs.items():
            node_name, style, label, stack = out_data
            h_edges.append(edge_string.format(start=comp_name, end=node_name))

        for comp_name, in_data in self.ins.items():
            node_name, style, label, stack = in_data
            v_edges.append(edge_string.format(start=comp_name, end=node_name))

        paths_str = '% Horizontal edges\n' + '\n'.join(h_edges) + '\n'

        paths_str += '% Vertical edges\n' + '\n'.join(v_edges) + ';'

        return paths_str


    def write(self, file_name, build=True):

        nodes = self._build_node_grid()
        edges = self._build_edges()

        module_path = os.path.dirname(__file__)
        diagram_border_path = os.path.join(module_path, 'diagram_border')
        diagram_styles_path = os.path.join(module_path, 'diagram_styles')

        tex_str = tex_template.format(nodes=nodes, edges=edges, diagram_border_path=diagram_border_path, diagram_styles_path=diagram_styles_path)

        f = open(file_name+'.tex','w')
        f.write(tex_str)
        f.close()

        if build:
            os.system('pdflatex ' + file_name + '.tex')



