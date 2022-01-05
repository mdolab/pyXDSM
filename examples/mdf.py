from pyxdsm.XDSM import XDSM, OPT, SOLVER, FUNC, LEFT

# Change `use_sfmath` to False to use computer modern
x = XDSM(use_sfmath=True)

x.add_system("opt", OPT, r"\text{Optimizer}")
x.add_system("solver", SOLVER, r"\text{Newton}")
x.add_system("D1", FUNC, "D_1")
x.add_system("D2", FUNC, "D_2")
x.add_system("F", FUNC, "F")
x.add_system("G", FUNC, "G")

x.connect("opt", "D1", "x, z")
x.connect("opt", "D2", "z")
x.connect("opt", "F", "x, z")
x.connect("solver", "D1", "y_2")
x.connect("solver", "D2", "y_1")
x.connect("D1", "solver", r"\mathcal{R}(y_1)")
x.connect("solver", "F", "y_1, y_2")
x.connect("D2", "solver", r"\mathcal{R}(y_2)")
x.connect("solver", "G", "y_1, y_2")

x.connect("F", "opt", "f")
x.connect("G", "opt", "g")

x.add_output("opt", "x^*, z^*", side=LEFT)
x.add_output("D1", "y_1^*", side=LEFT)
x.add_output("D2", "y_2^*", side=LEFT)
x.add_output("F", "f^*", side=LEFT)
x.add_output("G", "g^*", side=LEFT)
x.write("mdf")
