from pyxdsm.XDSM import XDSM, OPT, SOLVER, FUNC, LEFT

# Change `use_sfmath` to False to use computer modern
x = XDSM(use_sfmath=True)

x.add_system("opt", OPT, r"\text{PDE SOLVER}")
x.add_system("D1", SOLVER, r"\text{Poisson's}")
x.add_system("D2", SOLVER, r"\text{Heat}")
x.add_system("D3", SOLVER, r"\text{Wave}")
x.add_system("F1", FUNC, r"\text{Gauss-Seidel}")
x.add_system("F2", FUNC, r"\text{Jacobi}")

x.add_system("F3", FUNC, r"\text{Explicit}")
x.add_system("F4", FUNC, r"\text{Implicit}")

x.add_system("F5", FUNC, r"\text{Explicit}")
x.add_system("F6", FUNC, r"\text{Implicit}")

x.connect("opt", "D1", r"\text{Initial conditions, domain}")
x.connect("opt", "D2", r"\text{Initial conditions, domain}")
x.connect("opt", "D3", r"\text{Initial conditions, domain}")

x.connect("D1", "F1", r"\text{input}")
x.connect("D1", "F2", r"\text{input}")

x.connect("D2", "F3", r"\text{input}")
x.connect("D2", "F4", r"\text{input}")

x.connect("D3", "F5", r"\text{input}")
x.connect("D3", "F6", r"\text{input}")

x.connect("F1", "D1", r"\text{Plot solution}")
x.connect("F2", "D1", r"\text{Plot solution}")

x.connect("F3", "D2", r"\text{Plot solution}")
x.connect("F4", "D2", r"\text{Plot solution}")

x.connect("F5", "D3", r"\text{input}")
x.connect("F6", "D3", r"\text{input}")

#x.connect("solver", "D1", r"x_1")
#x.connect("solver", "D2", r"x_2")
#x.connect("solver", "D3", r"x_3")

#x.connect("D1", "D3", r"a_2")
#x.connect("D1", "D4", r"a_3")

#x.connect("D3", "D4", r"p")


#x.connect("D2", "D3", r"s_1")
#x.connect("D2", "D4", r"s_2")

#x.connect("D4", "D1", r"T_1")
#x.connect("D4", "D2", r"T_2")
#x.connect("D4", "D3", r"T_3")

#x.connect("D4", "opt", "Fuel burn")

#x.add_output("F1", r"\text{Plot solution}", side=LEFT)
#x.add_output("F2", r"\text{Plot solution}", side=LEFT)

#x.add_output("F3", r"\text{Plot solution}", side=LEFT)
#x.add_output("F4", r"\text{Plot solution}", side=LEFT)

#x.add_output("F5", r"\text{Plot solution}", side=LEFT)
#x.add_output("F6", r"\text{Plot solution}", side=LEFT)

x.write("pde_suite")
