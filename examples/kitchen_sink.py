from pyxdsm.XDSM import (
    XDSM,
    OPT,
    SUBOPT,
    SOLVER,
    DOE,
    IFUNC,
    FUNC,
    GROUP,
    IGROUP,
    METAMODEL,
    LEFT,
    RIGHT,
)

x = XDSM()

x.add_system("opt", OPT, r"\text{Optimizer}")
x.add_system("DOE", DOE, r"\text{DOE}")
x.add_system("MDA", SOLVER, r"\text{Newton}")
x.add_system("D1", FUNC, "D_1")

# can fade out blocks to allow for emphasis on sub-sections of XDSM
x.add_system("D2", IFUNC, "D_2", faded=True)

x.add_system("D3", IFUNC, "D_3")
x.add_system("subopt", SUBOPT, "SubOpt")
x.add_system("G1", GROUP, "G_1")
x.add_system("G2", IGROUP, "G_2")
x.add_system("MM", METAMODEL, "MM")

# if you give the label as a list or tuple, it splits it onto multiple lines
x.add_system("F", FUNC, ("F", r"\text{Functional}"))

# stacked can be used to represent multiple instances that can be run in parallel
x.add_system("H", FUNC, "H", stack=True)

x.add_process(
    ["opt", "DOE", "MDA", "D1", "D2", "subopt", "G1", "G2", "MM", "F", "H", "opt"],
    arrow=True,
)

x.connect("opt", "D1", ["x", "z", "y_2"], label_width=2)
x.connect("opt", "D2", ["z", "y_1"])
x.connect("opt", "D3", "z, y_1")
x.connect("opt", "subopt", "z, y_1")
x.connect("subopt", "G1", "z_2")
x.connect("subopt", "G2", "z_2")
x.connect("subopt", "MM", "z_2")
x.connect("opt", "G2", "z")
x.connect("opt", "F", "x, z")
x.connect("opt", "F", "y_1, y_2")

# you can also stack variables
x.connect("opt", "H", "y_1, y_2", stack=True)

x.connect("D1", "opt", r"\mathcal{R}(y_1)")
x.connect("D2", "opt", r"\mathcal{R}(y_2)")

x.connect("F", "opt", "f")
x.connect("H", "opt", "h", stack=True)

# can specify inputs to represent external information coming into the XDSM
x.add_input("D1", "P_1")
x.add_input("D2", "P_2")
x.add_input("opt", r"x_0", stack=True)

# can put outputs on the left or right sides
x.add_output("opt", r"x^*, z^*", side=RIGHT)
x.add_output("D1", r"y_1^*", side=LEFT)
x.add_output("D2", r"y_2^*", side=LEFT)
x.add_output("F", r"f^*", side=RIGHT)
x.add_output("H", r"h^*", side=RIGHT)
x.add_output("opt", r"y^*", side=LEFT)

x.add_process(["output_opt", "opt", "left_output_opt"])

x.write("kitchen_sink", cleanup=False)
x.write_sys_specs("sink_specs")
