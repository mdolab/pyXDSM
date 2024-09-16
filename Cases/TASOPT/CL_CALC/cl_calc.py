from pyxdsm.XDSM import XDSM, OPT, SOLVER, FUNC, LEFT

# Change `use_sfmath` to False to use computer modern
x = XDSM(use_sfmath=True)

#x.add_system("opt", OPT, r"\text{Optimizer}")
x.add_system("solver", OPT, r"\text{TASOPT}")
x.add_system("D1", SOLVER, "Geometry")
x.add_system("D2", SOLVER, "Flow")
x.add_system("D3", SOLVER, "Aero")
x.add_system("D4", FUNC, "Lift")
x.add_system("D5", FUNC, "Drag")
#x.add_system("F", FUNC, "F")
#x.add_system("G", FUNC, "G")

#x.connect("opt", "D1", "x, z")
#x.connect("opt", "D2", "z")
#x.connect("opt", "F", "x, z")

x.connect("solver", "D1", "Initial Design")
x.connect("solver", "D2", "Ma")

x.connect("solver", "D5", "a_{Re}, Re_{ref}")

x.connect("D1", "D3", r"\Lambda, S, K_P, b, c_o, P(\eta), C(\eta)")

x.connect("D1", "D5", r"t/c")

x.connect("D1", "D2", r"\Lambda, c")

x.connect("D2", "D5", r"Ma_{\perp}, Re_c")

x.connect("D3", "D4", r"C_L, C_{L_H}, \Lambda, S, K_P, v, c_o, P(\eta), C(\eta)")

x.connect("D4", "D5", r"c_l")


#x.connect("solver", "D2", r"C_L, C_{L_H}, \Lambda, S, K_P, v, c_o, P(\eta), C(\eta)")



#x.connect("D3", "D4", r"c_{l_\perp}")

#x.connect("solver", "D2", "y_1")
#x.connect("D1", "solver", r"\mathcal{R}(y_1)")
#x.connect("solver", "F", "y_1, y_2")
#x.connect("D2", "solver", r"\mathcal{R}(y_2)")
#x.connect("solver", "G", "y_1, y_2")

#x.connect("F", "opt", "f")
#x.connect("G", "opt", "g")

#x.add_output("opt", "x^*, z^*", side=LEFT)
#x.add_output("D1", "y_1^*", side=LEFT)
#x.add_output("D2", "y_2^*", side=LEFT)
x.add_output("D5", "c_{d_f}, c_{d_p}", side=LEFT)
#x.add_output("F", "f^*", side=LEFT)
#x.add_output("G", "g^*", side=LEFT)
x.write("cal_calc")
