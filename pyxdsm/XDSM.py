"""
pyXDSM with Pydantic models for validation and serialization
"""

import json
import os
from pathlib import Path
from typing import Literal, Optional, Union

from pydantic import BaseModel, field_validator, model_validator

from pyxdsm.xdsm_latex_writer import XDSMLatexWriter

# Constants
OPT = "Optimization"
SUBOPT = "SubOptimization"
SOLVER = "MDA"
DOE = "DOE"
IFUNC = "ImplicitFunction"
FUNC = "Function"
GROUP = "Group"
IGROUP = "ImplicitGroup"
METAMODEL = "Metamodel"
LEFT = "left"
RIGHT = "right"

ConnectionStyle = Literal["DataInter", "DataIO"]
Side = Literal["left", "right"]
AutoFadeOption = Literal["all", "connected", "none", "incoming", "outgoing"]

# Valid TikZ node styles (from diagram_styles.tikzstyles)
NodeStyle = Literal[
    "Optimization",
    "SubOptimization",
    "MDA",
    "DOE",
    "ImplicitFunction",
    "Function",
    "Group",
    "ImplicitGroup",
    "Metamodel",
    "DataInter",
    "DataIO",
]


class SystemNode(BaseModel):
    """System node on the diagonal of XDSM diagram."""

    node_name: str
    style: NodeStyle
    label: Union[str, list[str], tuple[str, ...]]
    stack: bool = False
    faded: bool = False
    label_width: Optional[int] = None
    spec_name: Optional[str] = None


    @field_validator("node_name")
    @classmethod
    def _validate_node_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Node name cannot be empty")
        return v.strip()

    @model_validator(mode='after')
    def set_defaults(self) -> 'SystemNode':
        """Set spec_name to node_name if not provided."""
        if self.spec_name is None:
            self.spec_name = self.node_name
        return self


class InputNode(BaseModel):
    """Input node at top of XDSM diagram."""

    node_name: str
    label: Union[str, list[str], tuple[str, ...]]
    label_width: Optional[int] = None
    style: str = "DataIO"
    stack: bool = False
    faded: bool = False


class OutputNode(BaseModel):
    """Output node on left or right side of XDSM diagram."""

    node_name: str
    label: Union[str, list[str], tuple[str, ...]]
    label_width: Optional[int] = None
    style: ConnectionStyle = "DataIO"
    stack: bool = False
    faded: bool = False
    side: Side = "right"


class ConnectionEdge(BaseModel):
    """Connection between two nodes."""

    src: str
    target: str
    label: Union[str, list[str], tuple[str, ...]]
    label_width: Optional[int] = None
    style: ConnectionStyle = "DataInter"
    stack: bool = False
    faded: bool = False
    src_faded: bool = False
    target_faded: bool = False


    @model_validator(mode="after")
    def _validate_no_self_connection(self):
        if self.src == self.target:
            raise ValueError("Cannot connect component to itself")
        return self


class ProcessChain(BaseModel):
    """Process flow chain between systems."""

    systems: list[str]
    arrow: bool = True
    faded: bool = False

    @field_validator("systems")
    @classmethod
    def _validate_systems(cls, v: list[str]) -> list[str]:
        if len(v) < 2:
            raise ValueError("Process chain must contain at least 2 systems")
        return v


class AutoFadeConfig(BaseModel):
    """Configuration for automatic fading of components."""

    inputs: AutoFadeOption = "none"
    outputs: AutoFadeOption = "none"
    connections: AutoFadeOption = "none"
    processes: AutoFadeOption = "none"

    @field_validator("inputs", "outputs", "processes")
    @classmethod
    def _validate_basic_options(cls, v: str) -> str:
        valid = ["all", "connected", "none"]
        if v not in valid:
            raise ValueError(f"Must be one of {valid}")
        return v

    @field_validator("connections")
    @classmethod
    def _validate_connection_options(cls, v: str) -> str:
        valid = ["all", "connected", "none", "incoming", "outgoing"]
        if v not in valid:
            raise ValueError(f"Must be one of {valid}")
        return v


class XDSM(BaseModel):
    """
    XDSM diagram specification and renderer using Pydantic validation.
    """

    systems: list[SystemNode] = []
    connections: list[ConnectionEdge] = []
    inputs: dict[str, InputNode] = {}
    outputs: dict[str, OutputNode] = {}
    processes: list[ProcessChain] = []

    use_sfmath: bool = True
    optional_packages: Union[str, list[str]] = []
    auto_fade: Union[dict[str, str], AutoFadeConfig] = AutoFadeConfig()

    @field_validator('optional_packages', mode='before')
    @classmethod
    def _validate_optional_packages(cls, v):
        """Accept string or list, convert to list."""
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return v

    @field_validator('auto_fade', mode='before')
    @classmethod
    def _validate_auto_fade(cls, v):
        """Accept dict or AutoFadeConfig, convert to AutoFadeConfig."""
        if v is None:
            return AutoFadeConfig()
        if isinstance(v, dict):
            return AutoFadeConfig(**v)
        return v

    @model_validator(mode="before")
    @classmethod
    def _set_defaults_for_missing_fields(cls, data):
        """Ensure missing or null collection fields get empty defaults."""
        if not isinstance(data, dict):
            return data

        # Set empty defaults for missing or null collection fields
        if "inputs" not in data or data.get("inputs") is None:
            data["inputs"] = {}
        if "outputs" not in data or data.get("outputs") is None:
            data["outputs"] = {}
        if "systems" not in data or data.get("systems") is None:
            data["systems"] = []
        if "connections" not in data or data.get("connections") is None:
            data["connections"] = []
        if "processes" not in data or data.get("processes") is None:
            data["processes"] = []

        return data

    @model_validator(mode="after")
    def _validate_unique_system_names(self):
        """Ensure all system names are unique."""
        names = [sys.node_name for sys in self.systems]
        duplicates = [n for n in names if names.count(n) > 1]
        if duplicates:
            raise ValueError(f"Duplicate system names: {set(duplicates)}")
        return self

    def add_system(
        self,
        node_name: str,
        style: str,
        label: Union[str, list[str], tuple[str, ...]],
        stack: bool = False,
        faded: bool = False,
        label_width: Optional[int] = None,
        spec_name: Optional[str] = None,
    ) -> None:
        r"""
        Add a "system" block, which will be placed on the diagonal of the XDSM diagram.

        Parameters
        ----------
        node_name : str
            The unique name given to this component

        style : str
            The type of the component

        label : str or list/tuple of strings
            The label to appear on the diagram. There are two options for this:
            - a single string
            - a list or tuple of strings, which is used for line breaking
            In either case, they should probably be enclosed in \text{} declarations to make sure
            the font is upright.

        stack : bool
            If true, the system will be displayed as several stacked rectangles,
            indicating the component is executed in parallel.

        faded : bool
            If true, the component will be faded, in order to highlight some other system.

        label_width : int or None
            If not None, AND if ``label`` is given as either a tuple or list, then this parameter
            controls how many items in the tuple/list will be displayed per line.
            If None, the label will be printed one item per line if given as a tuple or list,
            otherwise the string will be printed on a single line.

        spec_name : str
            The spec name used for the spec file.

        """
        system = SystemNode(
            node_name=node_name,
            style=style,
            label=label,
            stack=stack,
            faded=faded,
            label_width=label_width,
            spec_name=spec_name,
        )
        self.systems.append(system)

    def add_input(
        self,
        name: str,
        label: Union[str, list[str], tuple[str, ...]],
        label_width: Optional[int] = None,
        style: str = "DataIO",
        stack: bool = False,
        faded: bool = False,
    ) -> None:
        r"""
        Add an input, which will appear in the top row of the diagram.

        Parameters
        ----------
        name : str
            The unique name given to this component

        label : str or list/tuple of strings
            The label to appear on the diagram. There are two options for this:
            - a single string
            - a list or tuple of strings, which is used for line breaking
            In either case, they should probably be enclosed in \text{} declarations to make sure
            the font is upright.

        label_width : int or None
            If not None, AND if ``label`` is given as either a tuple or list, then this parameter
            controls how many items in the tuple/list will be displayed per line.
            If None, the label will be printed one item per line if given as a tuple or list,
            otherwise the string will be printed on a single line.

        style : str
            The style given to this component. Can be one of ['DataInter', 'DataIO']

        stack : bool
            If true, the system will be displayed as several stacked rectangles,
            indicating the component is executed in parallel.

        faded : bool
            If true, the component will be faded, in order to highlight some other system.
        """
        sys_faded = {s.node_name: s.faded for s in self.systems}

        if (self.auto_fade.inputs == "all") or (
            self.auto_fade.inputs == "connected" and name in sys_faded and sys_faded[name]
        ):
            faded = True

        self.inputs[name] = InputNode(
            node_name="output_" + name, label=label, label_width=label_width, style=style, stack=stack, faded=faded
        )

    def add_output(
        self,
        name: str,
        label: Union[str, list[str], tuple[str, ...]],
        label_width: Optional[int] = None,
        style: str = "DataIO",
        stack: bool = False,
        faded: bool = False,
        side: str = "left",
    ) -> None:
        r"""
        Add an output, which will appear in the left or right-most column of the diagram.

        Parameters
        ----------
        name : str
            The unique name given to this component

        label : str or list/tuple of strings
            The label to appear on the diagram. There are two options for this:
            - a single string
            - a list or tuple of strings, which is used for line breaking
            In either case, they should probably be enclosed in \text{} declarations to make sure
            the font is upright.

        label_width : int or None
            If not None, AND if ``label`` is given as either a tuple or list, then this parameter
            controls how many items in the tuple/list will be displayed per line.
            If None, the label will be printed one item per line if given as a tuple or list,
            otherwise the string will be printed on a single line.

        style : str
            The style given to this component. Can be one of ``['DataInter', 'DataIO']``

        stack : bool
            If true, the system will be displayed as several stacked rectangles,
            indicating the component is executed in parallel.

        faded : bool
            If true, the component will be faded, in order to highlight some other system.

        side : str
            Must be one of ``['left', 'right']``. This parameter controls whether the output
            is placed on the left-most column or the right-most column of the diagram.
        """
        sys_faded = {s.node_name: s.faded for s in self.systems}

        if (self.auto_fade.outputs == "all") or (
            self.auto_fade.outputs == "connected" and name in sys_faded and sys_faded[name]
        ):
            faded = True

        output = OutputNode(
            node_name=f"{side}_output_{name}",
            label=label,
            label_width=label_width,
            style=style,
            stack=stack,
            faded=faded,
            side=side,
        )

        self.outputs[name] = output

    def connect(
        self,
        src: str,
        target: str,
        label: Union[str, list[str], tuple[str, ...]],
        label_width: Optional[int] = None,
        style: str = "DataInter",
        stack: bool = False,
        faded: bool = False,
    ) -> None:
        r"""
        Connects two components with a data line, and adds a label to indicate
        the data being transferred.

        Parameters
        ----------
        src : str
            The name of the source component.

        target : str
            The name of the target component.

        label : str or list/tuple of strings
            The label to appear on the diagram. There are two options for this:
            - a single string
            - a list or tuple of strings, which is used for line breaking
            In either case, they should probably be enclosed in \text{} declarations to make sure
            the font is upright.

        label_width : int or None
            If not None, AND if ``label`` is given as either a tuple or list, then this parameter
            controls how many items in the tuple/list will be displayed per line.
            If None, the label will be printed one item per line if given as a tuple or list,
            otherwise the string will be printed on a single line.

        style : str
            The style given to this component. Can be one of ``['DataInter', 'DataIO']``

        stack : bool
            If true, the system will be displayed as several stacked rectangles,
            indicating the component is executed in parallel.

        faded : bool
            If true, the component will be faded, in order to highlight some other system.
        """
        sys_faded = {s.node_name: s.faded for s in self.systems}

        src_faded = src in sys_faded and sys_faded[src]
        target_faded = target in sys_faded and sys_faded[target]

        all_faded = self.auto_fade.connections == "all"
        if (
            all_faded
            or (self.auto_fade.connections == "connected" and src_faded and target_faded)
            or (self.auto_fade.connections == "incoming" and target_faded)
            or (self.auto_fade.connections == "outgoing" and src_faded)
        ):
            faded = True

        connection = ConnectionEdge(
            src=src,
            target=target,
            label=label,
            label_width=label_width,
            style=style,
            stack=stack,
            faded=faded,
            src_faded=src_faded,
            target_faded=target_faded,
        )
        self.connections.append(connection)

    def add_process(self, systems: list[str], arrow: bool = True, faded: bool = False) -> None:
        """
        Add a process line between a list of systems, to indicate process flow.

        Parameters
        ----------
        systems : list
            The names of the components, in the order in which they should be connected.
            For a complete cycle, repeat the first component as the last component.

        arrow : bool
            If true, arrows will be added to the process lines to indicate the direction
            of the process flow.
        """
        sys_faded = {s.node_name: s.faded for s in self.systems}

        if (self.auto_fade.processes == "all") or (
            self.auto_fade.processes == "connected" and any([sys_faded.get(s, False) for s in systems])
        ):
            faded = True

        process = ProcessChain(systems=systems, arrow=arrow, faded=faded)
        self.processes.append(process)

    def write(
        self, file_name: str, build: bool = True, cleanup: bool = True, quiet: bool = False, outdir: str = "."
    ) -> None:
        """
        Write output files for the XDSM diagram (delegates to XDSMLatexWriter).

        Parameters
        ----------
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
        XDSMLatexWriter.write(self, file_name, build, cleanup, quiet, outdir)

    def to_latex(
        self, file_name: str, build: bool = True, cleanup: bool = True, quiet: bool = False, outdir: str = "."
    ) -> None:
        """
        Export XDSM diagram to LaTeX/TikZ format.

        Alias for write() method for clarity when exporting to LaTeX.

        Parameters
        ----------
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
        XDSMLatexWriter.write(self, file_name, build, cleanup, quiet, outdir)

    def write_sys_specs(self, folder_name: str) -> None:
        """
        Write I/O spec json files for systems to specified folder

        An I/O spec of a system is the collection of all variables going into and out of it.
        That includes any variables being passed between systems, as well as all inputs and outputs.
        This information is useful for comparing implementations (such as components and groups in OpenMDAO)
        to the XDSM diagrams.

        The json spec files can be used to write testing utilities that compare the inputs/outputs of an implementation
        to the XDSM, and thus allow you to verify that your codes match the XDSM diagram precisely.
        This technique is especially useful when large engineering teams are collaborating on
        model development. It allows them to use the XDSM as a shared contract between team members
        so everyone can be sure that their codes will sync up.

        Parameters
        ----------
        folder_name: str
            name of the folder, which will be created if it doesn't exist, to put spec files into
        """

        def _label_to_spec(label: Union[str, list[str], tuple[str, ...]], spec: set[str]) -> None:
            """Add label variables to spec set."""
            if isinstance(label, str):
                label = [label]
            for var in label:
                if var:
                    spec.add(var)

        specs = {}
        for sys in self.systems:
            specs[sys.node_name] = {"inputs": set(), "outputs": set()}

        # Add inputs from Input nodes
        for sys_name, inp in self.inputs.items():
            _label_to_spec(inp.label, specs[sys_name]["inputs"])

        # Add inputs/outputs from Connections
        for conn in self.connections:
            _label_to_spec(conn.label, specs[conn.target]["inputs"])
            _label_to_spec(conn.label, specs[conn.src]["outputs"])

        # Add outputs from Output nodes
        for sys_name, out in self.outputs.items():
            _label_to_spec(out.label, specs[sys_name]["outputs"])

        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)

        for sys in self.systems:
            if sys.spec_name is not False and sys.spec_name is not None:
                path = os.path.join(folder_name, sys.spec_name + ".json")
                with open(path, "w") as f:
                    spec = specs[sys.node_name]
                    spec["inputs"] = list(spec["inputs"])
                    spec["outputs"] = list(spec["outputs"])
                    json_str = json.dumps(spec, indent=2)
                    f.write(json_str)

    def to_json(self, filename: Optional[str] = None) -> str:
        """
        Get the JSON representation of the XDSM, and optioally write to file.

        Parameters
        ----------
        filename : str
            The filename to which to write the JSON representation of the XDSM"""
        json_str = self.model_dump_json(indent=2)
        if filename:
            with open(filename, "w") as f:
                f.write(f"{json_str}\n")
        return json_str

    @classmethod
    def from_json(cls, s: str) -> "XDSM":
        """Instantiate an XDSM from the given JSON data.

        Parameters
        ----------
        f : str
            A filename or string of JSON data from which
            the XDSM should be instantiated.
        """
        if Path(s).is_file():
            with open(s) as f:
                try:
                    data = json.load(f)
                except Exception as e:
                    raise RuntimeError('Unable to load JSON from file: {s}') from e
        else:
            try:
                data = json.loads(s)
            except (json.JSONDecodeError, TypeError) as e:
                raise RuntimeError('Given string is neither an existing filename nor valid JSON.') from e
        return cls.model_validate(data)
