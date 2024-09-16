from pyxdsm.XDSM import XDSM, OPT, SOLVER, FUNC, LEFT

# Change `use_sfmath` to False to use computer modern
x = XDSM(use_sfmath=True)

x.add_system("opt", OPT, r"\text{Optimizer}")
x.add_system("ops", OPT, r"\text{OPERATIONS}")
x.add_system("fin", OPT, r"\text{FINANCE}")
x.add_system("solver", OPT, r"\text{TASOPT}")
x.add_system("D1", SOLVER, r"\text{Aerodynamics}")
x.add_system("D2", SOLVER, r"\text{Structures}")
x.add_system("D3", SOLVER, r"\text{Propulsion}")
x.add_system("D4", SOLVER, r"\text{Trajectory}")
x.add_system("D5", SOLVER, r"\text{Emissions}")

x.connect("opt", "ops", r"x_0, \text{number of flights, passenger count}")

x.connect("ops", "solver", r"x_0")

x.connect("solver", "D1", r"x_1")
x.connect("solver", "D2", r"x_2")
x.connect("solver", "D3", r"x_3")

x.connect("D1", "D2", r"a_1")
x.connect("D1", "D3", r"a_2")
x.connect("D1", "D4", r"a_3")

x.connect("D3", "D4", r"p")


x.connect("D2", "D3", r"s_1")
x.connect("D2", "D4", r"s_2")

x.connect("D4", "D1", r"T_1")
x.connect("D4", "D2", r"T_2")
x.connect("D4", "D3", r"T_3")

x.connect("D4", "fin", r"\text{Fuel burn, flight time}")
x.connect("D4", "D5", r"\text{Fuel burn, altitude}")
x.connect("fin", "ops", "D.O.C")

x.connect("D5", "ops", r"CO_2,NO_x")

x.connect("ops", "opt", r"D.O.C,CO_2,NO_x")

x.add_output("opt", "x^*", side=LEFT)

x.write("doc_emission")
