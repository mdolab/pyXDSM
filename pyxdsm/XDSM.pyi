from typing import Iterator, NamedTuple, Literal, Sequence

OPT: str
SUBOPT: str
SOLVER: str
DOE: str
IFUNC: str
FUNC: str
GROUP: str
IGROUP: str
METAMODEL: str
LEFT: str
RIGHT: str

tikzpicture_template: str
tex_template: str

def chunk_label(label: str, n_chunks: int) -> Iterator[str]: ...
def _parse_label(
    label: str | list[str] | tuple[str, ...], label_width: int | None = ...
) -> str: ...
def _label_to_spec(label: str | list[str], spec: set[str]) -> None: ...

class System(NamedTuple):
    node_name: str
    style: str
    label: str | list[str]
    stack: bool
    faded: bool
    label_width: int | None
    spec_name: str

class Input(NamedTuple):
    node_name: str
    label: str | list[str]
    label_width: int | None
    style: str
    stack: bool
    faded: bool

class Output(NamedTuple):
    node_name: str
    label: str | list[str]
    label_width: int | None
    style: str
    stack: bool
    faded: bool
    side: Literal["left", "right"]

class Connection(NamedTuple):
    src: str
    target: str
    label: str | list[str]
    label_width: int | None
    style: str
    stack: bool
    faded: bool
    src_faded: bool
    target_faded: bool

class Process(NamedTuple):
    systems: list[str]
    arrow: str
    faded: bool

class XDSM:
    systems: list[System]
    connections: list[Connection]
    left_outs: dict[str, Output]
    right_outs: dict[str, Output]
    ins: dict[str, Input]
    processes: list[Process]
    use_sfmath: bool
    optional_packages: list[str]
    auto_fade: dict[str, str]

    def __init__(
        self,
        use_sfmath: bool = ...,
        optional_latex_packages: str | list[str] | None = ...,
        auto_fade: dict[str, str] | None = ...,
    ) -> None: ...
    def add_system(
        self,
        node_name: str,
        style: str,
        label: str | list[str] | tuple[str, ...],
        stack: bool = ...,
        faded: bool = ...,
        label_width: int | None = ...,
        spec_name: str | None = ...,
    ) -> None: ...
    def add_input(
        self,
        name: str,
        label: str | list[str] | tuple[str, ...],
        label_width: int | None = None,
        style: str = "DataIO",
        stack: bool = False,
        faded: bool = False,
    ) -> None: ...
    def add_output(
        self,
        name: str,
        label: str | list[str] | tuple[str, ...],
        label_width: int | None = None,
        style: str = "DataIO",
        stack: bool = False,
        faded: bool = False,
        side: Literal["left", "right"] = "left",
    ) -> None: ...
    def connect(
        self,
        src: str,
        target: str,
        label: str | list[str] | tuple[str, ...],
        label_width: int | None = None,
        style: str = "DataInter",
        stack: bool = False,
        faded: bool = False,
    ) -> None: ...
    def add_process(
        self,
        systems: Sequence[str],
        arrow: bool = True,
        faded: bool = False,
    ) -> None: ...
    # def _build_node_grid(self) -> str: ...
    # def _build_edges(self) -> str: ...
    # def _build_process_chain(self) -> str: ...
    # def _compose_optional_package_list(self) -> str: ...
    def write(
        self,
        file_name: str,
        build: bool = True,
        cleanup: bool = True,
        quiet: bool = False,
        outdir: str = ".",
    ) -> None: ...
    def write_sys_specs(
        self,
        folder_name: str,
    ) -> None: ...
