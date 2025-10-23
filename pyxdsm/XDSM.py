"""
pyXDSM with Pydantic models for validation and serialization
"""

import json
import os
from typing import Dict, List, Literal, Optional, Set, Tuple, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

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

# Type definitions - these match the TikZ styles in diagram_styles
NodeType = Literal['Optimization', 'SubOptimization', 'MDA', 'DOE', 'ImplicitFunction',
                   'Function', 'Group', 'ImplicitGroup', 'Metamodel']
ConnectionStyle = Literal['DataInter', 'DataIO']
Side = Literal['left', 'right']
AutoFadeOption = Literal['all', 'connected', 'none', 'incoming', 'outgoing']

# Valid TikZ node styles (from diagram_styles.tikzstyles)
VALID_NODE_STYLES = {
    'Optimization', 'SubOptimization', 'MDA', 'DOE', 'ImplicitFunction',
    'Function', 'Group', 'ImplicitGroup', 'Metamodel', 'DataInter', 'DataIO'
}


class SystemNode(BaseModel):
    """System node on the diagonal of XDSM diagram."""

    node_name: str = Field(..., description="Unique name for the system")
    style: str = Field(..., description="Type/style of the system")
    label: Union[str, List[str], Tuple[str, ...]] = Field(..., description="Display label")
    stack: bool = Field(default=False, description="Display as stacked rectangles")
    faded: bool = Field(default=False, description="Fade the component")
    label_width: Optional[int] = Field(default=None, description="Number of items per line")
    spec_name: Optional[str] = Field(default=None, description="Name for spec file")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator('node_name')
    @classmethod
    def _validate_node_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Node name cannot be empty")
        return v.strip()

    @field_validator('style')
    @classmethod
    def _validate_style(cls, v: str) -> str:
        """Validate that style is a known TikZ style."""
        if v not in VALID_NODE_STYLES:
            raise ValueError(
                f"Style '{v}' is not a valid TikZ style. "
                f"Valid styles are: {', '.join(sorted(VALID_NODE_STYLES))}"
            )
        return v

    def __init__(self, **data):
        super().__init__(**data)
        if self.spec_name is None:
            self.spec_name = self.node_name


class InputNode(BaseModel):
    """Input node at top of XDSM diagram."""

    node_name: str = Field(..., description="Internal node name")
    label: Union[str, List[str], Tuple[str, ...]] = Field(..., description="Display label")
    label_width: Optional[int] = Field(default=None, description="Number of items per line")
    style: str = Field(default="DataIO", description="Node style")
    stack: bool = Field(default=False, description="Display as stacked rectangles")
    faded: bool = Field(default=False, description="Fade the component")

    model_config = ConfigDict(arbitrary_types_allowed=True)


class OutputNode(BaseModel):
    """Output node on left or right side of XDSM diagram."""

    node_name: str = Field(..., description="Internal node name")
    label: Union[str, List[str], Tuple[str, ...]] = Field(..., description="Display label")
    label_width: Optional[int] = Field(default=None, description="Number of items per line")
    style: str = Field(default="DataIO", description="Node style")
    stack: bool = Field(default=False, description="Display as stacked rectangles")
    faded: bool = Field(default=False, description="Fade the component")
    side: Side = Field(..., description="Which side (left or right)")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator('side')
    @classmethod
    def _validate_side(cls, v: str) -> str:
        if v not in ['left', 'right']:
            raise ValueError("Side must be 'left' or 'right'")
        return v


class ConnectionEdge(BaseModel):
    """Connection between two nodes."""

    src: str = Field(..., description="Source node name")
    target: str = Field(..., description="Target node name")
    label: Union[str, List[str], Tuple[str, ...]] = Field(..., description="Connection label")
    label_width: Optional[int] = Field(default=None, description="Number of items per line")
    style: str = Field(default="DataInter", description="Connection style")
    stack: bool = Field(default=False, description="Display as stacked")
    faded: bool = Field(default=False, description="Fade the connection")
    src_faded: bool = Field(default=False, description="Source node is faded")
    target_faded: bool = Field(default=False, description="Target node is faded")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator('label_width')
    @classmethod
    def _validate_label_width(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not isinstance(v, int):
            raise ValueError("label_width must be an integer")
        return v

    @model_validator(mode='after')
    def _validate_no_self_connection(self):
        if self.src == self.target:
            raise ValueError("Cannot connect component to itself")
        return self


class ProcessChain(BaseModel):
    """Process flow chain between systems."""

    systems: List[str] = Field(..., description="List of system names in order")
    arrow: bool = Field(default=True, description="Show arrows on process lines")
    faded: bool = Field(default=False, description="Fade the process chain")

    @field_validator('systems')
    @classmethod
    def _validate_systems(cls, v: List[str]) -> List[str]:
        if len(v) < 2:
            raise ValueError("Process chain must contain at least 2 systems")
        return v


class AutoFadeConfig(BaseModel):
    """Configuration for automatic fading of components."""

    inputs: AutoFadeOption = Field(default='none', description="Auto-fade inputs")
    outputs: AutoFadeOption = Field(default='none', description="Auto-fade outputs")
    connections: AutoFadeOption = Field(default='none', description="Auto-fade connections")
    processes: AutoFadeOption = Field(default='none', description="Auto-fade processes")

    @field_validator('inputs', 'outputs', 'processes')
    @classmethod
    def _validate_basic_options(cls, v: str) -> str:
        valid = ['all', 'connected', 'none']
        if v not in valid:
            raise ValueError(f"Must be one of {valid}")
        return v

    @field_validator('connections')
    @classmethod
    def _validate_connection_options(cls, v: str) -> str:
        valid = ['all', 'connected', 'none', 'incoming', 'outgoing']
        if v not in valid:
            raise ValueError(f"Must be one of {valid}")
        return v


class XDSM(BaseModel):
    """
    XDSM diagram specification and renderer using Pydantic validation.
    """

    systems: List[SystemNode] = Field(default_factory=list, description="System nodes")
    connections: List[ConnectionEdge] = Field(default_factory=list, description="Connections")
    inputs: Dict[str, InputNode] = Field(default_factory=dict, description="Input nodes")
    outputs: Dict[str, OutputNode] = Field(default_factory=dict, description="Left output nodes")
    processes: List[ProcessChain] = Field(default_factory=list, description="Process chains")

    use_sfmath: bool = Field(default=True, description="Use sfmath LaTeX package")
    optional_packages: List[str] = Field(default_factory=list, description="Additional LaTeX packages")
    auto_fade: AutoFadeConfig = Field(default_factory=AutoFadeConfig, description="Auto-fade configuration")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, use_sfmath: bool = True,
                 optional_latex_packages: Optional[Union[str, List[str]]] = None,
                 auto_fade: Optional[Dict[str, str]] = None,
                 **data):
        """
        Initialize XDSM object.

        Parameters
        ----------
        use_sfmath : bool
            Whether to use the sfmath latex package
        optional_latex_packages : str or list of strings
            Additional latex packages for PDF/TEX generation
        auto_fade : dict
            Auto-fade configuration with keys: inputs, outputs, connections, processes
        """
        # Only process if these aren't already in data (from deserialization)
        if 'optional_packages' not in data:
            # Process optional packages
            packages = []
            if optional_latex_packages is not None:
                if isinstance(optional_latex_packages, str):
                    packages = [optional_latex_packages]
                elif isinstance(optional_latex_packages, list):
                    packages = optional_latex_packages
                else:
                    raise ValueError("optional_latex_packages must be a string or list of strings")
            data['optional_packages'] = packages

        if 'auto_fade' not in data:
            # Process auto_fade
            fade_config = AutoFadeConfig()
            if auto_fade is not None:
                fade_config = AutoFadeConfig(**auto_fade)
            data['auto_fade'] = fade_config

        if 'use_sfmath' not in data:
            data['use_sfmath'] = use_sfmath

        super().__init__(**data)

    @model_validator(mode='before')
    @classmethod
    def _set_defaults_for_missing_fields(cls, data):
        """Ensure missing or null collection fields get empty defaults."""
        if not isinstance(data, dict):
            return data

        # Set empty defaults for missing or null collection fields
        if 'inputs' not in data or data.get('inputs') is None:
            data['inputs'] = {}
        if 'outputs' not in data or data.get('outputs') is None:
            data['outputs'] = {}
        if 'systems' not in data or data.get('systems') is None:
            data['systems'] = []
        if 'connections' not in data or data.get('connections') is None:
            data['connections'] = []
        if 'processes' not in data or data.get('processes') is None:
            data['processes'] = []

        return data

    @model_validator(mode='after')
    def _validate_unique_system_names(self):
        """Ensure all system names are unique."""
        names = [sys.node_name for sys in self.systems]
        duplicates = [n for n in names if names.count(n) > 1]
        if duplicates:
            raise ValueError(f"Duplicate system names: {set(duplicates)}")
        return self

    def add_system(self, node_name: str, style: str, label: Union[str, List[str], Tuple[str, ...]],
                   stack: bool = False, faded: bool = False, label_width: Optional[int] = None,
                   spec_name: Optional[str] = None) -> None:
        """Add a system block on the diagonal."""
        system = SystemNode(
            node_name=node_name,
            style=style,
            label=label,
            stack=stack,
            faded=faded,
            label_width=label_width,
            spec_name=spec_name
        )
        self.systems.append(system)

    def add_input(self, name: str, label: Union[str, List[str], Tuple[str, ...]],
                  label_width: Optional[int] = None, style: str = "DataIO",
                  stack: bool = False, faded: bool = False) -> None:
        """Add an input node at the top."""
        sys_faded = {s.node_name: s.faded for s in self.systems}

        if (self.auto_fade.inputs == "all") or \
           (self.auto_fade.inputs == "connected" and name in sys_faded and sys_faded[name]):
            faded = True

        self.inputs[name] = InputNode(
            node_name="output_" + name,
            label=label,
            label_width=label_width,
            style=style,
            stack=stack,
            faded=faded
        )

    def add_output(self, name: str, label: Union[str, List[str], Tuple[str, ...]],
                   label_width: Optional[int] = None, style: str = "DataIO",
                   stack: bool = False, faded: bool = False, side: str = "left") -> None:
        """Add an output node on the left or right side."""
        sys_faded = {s.node_name: s.faded for s in self.systems}

        if (self.auto_fade.outputs == "all") or \
           (self.auto_fade.outputs == "connected" and name in sys_faded and sys_faded[name]):
            faded = True

        output = OutputNode(
            node_name=f"{side}_output_{name}",
            label=label,
            label_width=label_width,
            style=style,
            stack=stack,
            faded=faded,
            side=side
        )

        self.outputs[name] = output

    def connect(self, src: str, target: str, label: Union[str, List[str], Tuple[str, ...]],
                label_width: Optional[int] = None, style: str = "DataInter",
                stack: bool = False, faded: bool = False) -> None:
        """Connect two components with a data line."""
        sys_faded = {s.node_name: s.faded for s in self.systems}

        src_faded = src in sys_faded and sys_faded[src]
        target_faded = target in sys_faded and sys_faded[target]

        all_faded = self.auto_fade.connections == "all"
        if (all_faded or
            (self.auto_fade.connections == "connected" and src_faded and target_faded) or
            (self.auto_fade.connections == "incoming" and target_faded) or
            (self.auto_fade.connections == "outgoing" and src_faded)):
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
            target_faded=target_faded
        )
        self.connections.append(connection)

    def add_process(self, systems: List[str], arrow: bool = True, faded: bool = False) -> None:
        """Add a process line between systems."""
        sys_faded = {s.node_name: s.faded for s in self.systems}

        if (self.auto_fade.processes == "all") or \
           (self.auto_fade.processes == "connected" and
            any([sys_faded.get(s, False) for s in systems])):
            faded = True

        process = ProcessChain(systems=systems, arrow=arrow, faded=faded)
        self.processes.append(process)

    def write(self, file_name: str, build: bool = True, cleanup: bool = True,
              quiet: bool = False, outdir: str = ".") -> None:
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

    def to_latex(self, file_name: str, build: bool = True, cleanup: bool = True,
                 quiet: bool = False, outdir: str = ".") -> None:
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
        Write I/O spec JSON files for systems.

        Parameters
        ----------
        folder_name : str
            Folder to write spec files into
        """
        def _label_to_spec(label: Union[str, List[str], Tuple[str, ...]], spec: Set[str]) -> None:
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
        """Export XDSM specification to JSON."""
        json_str = self.model_dump_json(indent=2)
        if filename:
            with open(filename, 'w') as f:
                f.write(json_str)
        return json_str

    @classmethod
    def from_json(cls, filename: str) -> 'XDSM':
        """Load XDSM from JSON file."""
        with open(filename) as f:
            data = json.load(f)
        return cls.model_validate(data)


# Example usage
if __name__ == "__main__":
    # Create XDSM with validation
    xdsm = XDSM(use_sfmath=True, auto_fade={'connections': 'connected'})

    # Add systems - note: use the proper style constants
    xdsm.add_system('opt', OPT, r'\text{Optimizer}')
    xdsm.add_system('d1', FUNC, r'\text{Discipline 1}')  # Changed to FUNC which is valid
    xdsm.add_system('d2', FUNC, r'\text{Discipline 2}')
    xdsm.add_system('func', FUNC, r'\text{Objective}')

    # Add connections
    xdsm.connect('opt', 'd1', r'x_1')
    xdsm.connect('opt', 'd2', r'x_2')
    xdsm.connect('d1', 'd2', r'y_1')
    xdsm.connect('d2', 'd1', r'y_2')
    xdsm.connect('d1', 'func', r'f_1')
    xdsm.connect('d2', 'func', r'f_2')
    xdsm.connect('func', 'opt', r'F')

    # Add process
    xdsm.add_process(['opt', 'd1', 'd2', 'func', 'opt'])

    # Export to JSON
    xdsm.to_json('xdsm_spec.json')

    # Write LaTeX files
    xdsm.write('example_xdsm', build=True)

    # Load from JSON
    xdsm_loaded = XDSM.from_json('xdsm_spec.json')
    print("Successfully loaded XDSM from JSON")

    # Validate example - this will raise an error
    try:
        bad_xdsm = XDSM()
        bad_xdsm.add_system('sys1', OPT, 'System 1')
        bad_xdsm.connect('sys1', 'sys1', 'Invalid')  # Self-connection error
    except ValueError as e:
        print(f"Validation caught error: {e}")
