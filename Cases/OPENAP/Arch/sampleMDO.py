from pyxdsm.XDSM import XDSM, OPT, SOLVER, FUNF, LEFT, GROUP, FUNS, FLUID, SOLID, PROPULSION

# Change `use_sfmath` to False to use computer modern
x = XDSM(use_sfmath=True)

x.add_system("adsb", OPT, r"\text{ADS-B}")
x.add_system("CIRIUM", OPT, r"\text{CIRIUM}")
x.add_system("openap", SOLVER, r"\text{OpenAP}")
x.add_system("fluid", FLUID, r"\text{FLUID}")
x.add_system("aero", FUNF, r"\text{Aerodynamics}")
x.add_system("kin", FUNS, r"\text{Kinematics}")
x.add_system("solid", SOLID, r"\text{SOLID}")
x.add_system("propulsion", PROPULSION, r"\text{PROPULSION}")
#x.add_system("engine", FUNF, r"\text{Engine}")
#x.add_system("traj", FUNF, r"\text{Trajectory}")


x.connect("adsb", "CIRIUM", r"\text{Flight Identifier}")
x.connect("adsb", "openap", r"\text{Mission parameters}")

#x.connect("CIRIUM", "engine", r"\text{Engine variant}")

#x.connect("openap", "aero", r"\text{Mission parameters, mass fraction}")
#x.connect("openap", "kin", r"\text{Mission parameters}")
#x.connect("openap", "engine", r"\text{Mission parameters, mass fraction}")

#x.connect("aero", "traj", r"\text{Lift, Drag}")
#x.connect("kin", "traj", r"\text{R.O.C, T.O. speed... }")
#x.connect("engine", "traj", r"\text{Avaiable thrust}")


#x.add_output("traj", r"\text{Fuel burn}", side=LEFT)

x.write("sampelMDO")
