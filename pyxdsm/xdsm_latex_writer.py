import os
import re
import subprocess
from typing import TYPE_CHECKING, List, Optional, Tuple, Union

import numpy as np

from pyxdsm import __version__ as pyxdsm_version

if TYPE_CHECKING:
    from pyxdsm.XDSM import XDSM

# LaTeX templates
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


def _chunk_label(label, n_chunks):
    for i in range(0, len(label), n_chunks):
        yield label[i : i + n_chunks]


def _sanitize_tikz_name(name: str) -> str:
    """
    Sanitize a node name to be TikZ-compatible.

    TikZ node names cannot contain certain characters like periods, spaces,
    and other special characters. This function replaces them with safe alternatives.

    Parameters
    ----------
    name : str
        Original node name (may contain periods, spaces, etc.)

    Returns
    -------
    str
        Sanitized name safe for use as TikZ node identifier
    """
    # Replace periods with underscores
    sanitized = name.replace('.', '_')
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    # Replace other problematic characters with underscores
    sanitized = re.sub(r'[^\w\-]', '_', sanitized)
    return sanitized


def _parse_label(label: Union[str, List[str], Tuple[str, ...]], label_width: Optional[int] = None) -> str:
    """Parse label into LaTeX format."""
    if isinstance(label, (tuple, list)):
        if label_width is None:
            return r"$\begin{array}{c}" + r" \\ ".join(label) + r"\end{array}$"
        else:
            labels = []
            for chunk in _chunk_label(label, label_width):
                labels.append(", ".join(chunk))
            return r"$\begin{array}{c}" + r" \\ ".join(labels) + r"\end{array}$"
    else:
        return rf"${label}$"


class XDSMLatexWriter:
    """
    Writer class for generating LaTeX/TikZ output from XDSM diagrams.
    """

    @staticmethod
    def _build_node_grid(xdsm: 'XDSM') -> str:
        """Build the TikZ node grid."""
        size = len(xdsm.systems)
        comps_rows = np.arange(size)
        comps_cols = np.arange(size)

        if xdsm.inputs:
            size += 1
            comps_rows += 1

        if any(out.side == "left" for out in xdsm.outputs.values()):
            size += 1
            comps_cols += 1

        if any(out.side == "right" for out in xdsm.outputs.values()):
            size += 1

        row_idx_map = {}
        col_idx_map = {}

        node_str = r"\node [{style}] ({node_name}) {{{node_label}}};"
        grid = np.empty((size, size), dtype=object)
        grid[:] = ""

        # Add diagonal systems
        for i_row, j_col, comp in zip(comps_rows, comps_cols, xdsm.systems):
            style = comp.style
            if comp.stack:
                style += ",stack"
            if comp.faded:
                style += ",faded"

            label = _parse_label(comp.label, comp.label_width)
            sanitized_name = _sanitize_tikz_name(comp.node_name)
            node = node_str.format(style=style, node_name=sanitized_name, node_label=label)
            grid[i_row, j_col] = node

            row_idx_map[comp.node_name] = i_row
            col_idx_map[comp.node_name] = j_col

        # Add off-diagonal connection nodes
        for conn in xdsm.connections:
            src_row = row_idx_map[conn.src]
            target_col = col_idx_map[conn.target]

            style = conn.style
            if conn.stack:
                style += ",stack"
            if conn.faded:
                style += ",faded"

            label = _parse_label(conn.label, conn.label_width)
            node_name = f"{_sanitize_tikz_name(conn.src)}-{_sanitize_tikz_name(conn.target)}"
            node = node_str.format(style=style, node_name=node_name, node_label=label)

            grid[src_row, target_col] = node

        # Add left outputs
        for comp_name, out in xdsm.outputs.items():
            if out.side != "left":
                continue
            style = out.style
            if out.stack:
                style += ",stack"
            if out.faded:
                style += ",faded"

            i_row = row_idx_map[comp_name]
            label = _parse_label(out.label, out.label_width)
            sanitized_name = _sanitize_tikz_name(out.node_name)
            node = node_str.format(style=style, node_name=sanitized_name, node_label=label)
            grid[i_row, 0] = node

        # Add right outputs
        for comp_name, out in xdsm.outputs.items():
            if out.side != "right":
                continue
            style = out.style
            if out.stack:
                style += ",stack"
            if out.faded:
                style += ",faded"

            i_row = row_idx_map[comp_name]
            label = _parse_label(out.label, out.label_width)
            sanitized_name = _sanitize_tikz_name(out.node_name)
            node = node_str.format(style=style, node_name=sanitized_name, node_label=label)
            grid[i_row, -1] = node

        # Add inputs
        for comp_name, inp in xdsm.inputs.items():
            style = inp.style
            if inp.stack:
                style += ",stack"
            if inp.faded:
                style += ",faded"

            j_col = col_idx_map[comp_name]
            label = _parse_label(inp.label, inp.label_width)
            sanitized_name = _sanitize_tikz_name(inp.node_name)
            node = node_str.format(style=style, node_name=sanitized_name, node_label=label)
            grid[0, j_col] = node

        # Convert grid to string
        rows_str = ""
        for i, row in enumerate(grid):
            rows_str += f"%Row {i}\n" + "&\n".join(row) + r"\\" + "\n"

        return rows_str

    @staticmethod
    def _build_edges(xdsm: 'XDSM') -> str:
        """Build the TikZ edge definitions."""
        h_edges = []
        v_edges = []

        edge_format = "({start}) edge [{style}] ({end})"

        for conn in xdsm.connections:
            h_style = "DataLine"
            v_style = "DataLine"

            if conn.src_faded or conn.faded:
                h_style += ",faded"
            if conn.target_faded or conn.faded:
                v_style += ",faded"

            src_sanitized = _sanitize_tikz_name(conn.src)
            target_sanitized = _sanitize_tikz_name(conn.target)
            od_node = f"{src_sanitized}-{target_sanitized}"
            h_edges.append(edge_format.format(start=src_sanitized, end=od_node, style=h_style))
            v_edges.append(edge_format.format(start=od_node, end=target_sanitized, style=v_style))

        for comp_name, out in xdsm.outputs.items():
            if out.side != "left":
                continue
            style = "DataLine"
            if out.faded:
                style += ",faded"
            comp_sanitized = _sanitize_tikz_name(comp_name)
            out_sanitized = _sanitize_tikz_name(out.node_name)
            h_edges.append(edge_format.format(start=comp_sanitized, end=out_sanitized, style=style))

        for comp_name, out in xdsm.outputs.items():
            if out.side != "right":
                continue
            style = "DataLine"
            if out.faded:
                style += ",faded"
            comp_sanitized = _sanitize_tikz_name(comp_name)
            out_sanitized = _sanitize_tikz_name(out.node_name)
            h_edges.append(edge_format.format(start=comp_sanitized, end=out_sanitized, style=style))

        for comp_name, inp in xdsm.inputs.items():
            style = "DataLine"
            if inp.faded:
                style += ",faded"
            comp_sanitized = _sanitize_tikz_name(comp_name)
            inp_sanitized = _sanitize_tikz_name(inp.node_name)
            v_edges.append(edge_format.format(start=comp_sanitized, end=inp_sanitized, style=style))

        h_edges = sorted(h_edges, key=lambda s: "faded" in s)
        v_edges = sorted(v_edges, key=lambda s: "faded" in s)

        paths_str = "% Horizontal edges\n" + "\n".join(h_edges) + "\n"
        paths_str += "% Vertical edges\n" + "\n".join(v_edges) + ";"

        return paths_str

    @staticmethod
    def _build_process_chain(xdsm: 'XDSM') -> str:
        """Build the TikZ process chain definitions."""
        sys_names = [s.node_name for s in xdsm.systems]
        output_names = (
            [inp.node_name for inp in xdsm.inputs.values()] +
            [out.node_name for out in xdsm.outputs.values()]
        )

        chain_str = ""

        for proc in xdsm.processes:
            chain_str += "\\begin{scope}[start chain=process]\n"
            chain_str += "\\begin{pgfonlayer}{process}\n"
            start_tip = False

            for i, sys in enumerate(proc.systems):
                if sys not in sys_names and sys not in output_names:
                    raise ValueError(f'Process includes system "{sys}" but no such system exists')

                if sys in output_names and i == 0:
                    start_tip = True

                sys_sanitized = _sanitize_tikz_name(sys)

                if i == 0:
                    chain_str += f"\\chainin ({sys_sanitized});\n"
                else:
                    if sys in output_names or (i == 1 and start_tip):
                        style = "ProcessTipA" if proc.arrow else "ProcessTip"
                    else:
                        style = "ProcessHVA" if proc.arrow else "ProcessHV"

                    if proc.faded:
                        style = "Faded" + style

                    chain_str += f"\\chainin ({sys_sanitized}) [join=by {style}];\n"

            chain_str += "\\end{pgfonlayer}\n"
            chain_str += "\\end{scope}\n"

        return chain_str

    @staticmethod
    def _compose_optional_package_list(xdsm: 'XDSM') -> str:
        """Compose the optional LaTeX package list."""
        packages = xdsm.optional_packages.copy()
        if xdsm.use_sfmath:
            packages.append("sfmath")
        return ",".join(packages)

    @staticmethod
    def write(xdsm: 'XDSM', file_name: str, build: bool = True, cleanup: bool = True,
              quiet: bool = False, outdir: str = ".") -> None:
        """
        Write output files for the XDSM diagram.

        Parameters
        ----------
        xdsm : XDSM
            The XDSM diagram object to write
        file_name : str
            Prefix for output files
        build : bool
            Whether to compile the PDF
        cleanup : bool
            Whether to delete build files after compilation
        quiet : bool
            Suppress pdflatex output
        outdir : str
            Output directory path
        """
        nodes = XDSMLatexWriter._build_node_grid(xdsm)
        edges = XDSMLatexWriter._build_edges(xdsm)
        process = XDSMLatexWriter._build_process_chain(xdsm)

        module_path = os.path.dirname(__file__)
        diagram_styles_path = os.path.join(module_path, "diagram_styles")
        diagram_styles_path = diagram_styles_path.replace("\\", "/")

        optional_packages_str = XDSMLatexWriter._compose_optional_package_list(xdsm)

        tikzpicture_str = tikzpicture_template.format(
            nodes=nodes,
            edges=edges,
            process=process,
            diagram_styles_path=diagram_styles_path,
            optional_packages=optional_packages_str,
        )

        base_output_fp = os.path.join(outdir, file_name)
        with open(base_output_fp + ".tikz", "w") as f:
            f.write(tikzpicture_str)

        tex_str = tex_template.format(
            nodes=nodes,
            edges=edges,
            tikzpicture_path=file_name + ".tikz",
            diagram_styles_path=diagram_styles_path,
            optional_packages=optional_packages_str,
            version=pyxdsm_version,
        )

        with open(base_output_fp + ".tex", "w") as f:
            f.write(tex_str)

        if build:
            command = [
                "pdflatex",
                "-halt-on-error",
                "-interaction=nonstopmode",
                f"-output-directory={outdir}",
            ]
            if quiet:
                command += ["-interaction=batchmode", "-halt-on-error"]
            command += [f"{file_name}.tex"]
            subprocess.run(command, check=True)

            if cleanup:
                for ext in ["aux", "fdb_latexmk", "fls", "log"]:
                    f_name = f"{base_output_fp}.{ext}"
                    if os.path.exists(f_name):
                        os.remove(f_name)
