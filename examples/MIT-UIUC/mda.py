from pyxdsm.XDSM import XDSM, OPT, SOLVER, FUNF, LEFT, GROUP, FUNS, FLUID, SOLID, PROPULSION

# Change `use_sfmath` to False to use computer modern
x = XDSM(use_sfmath=True)

#-------------------------DIAGONAL BLOCK DEFINITION--------------------------#
# Add optimizer
x.add_system("Optimizer", OPT, r"\text{Optimizer}")

# Add MDA block
x.add_system("MDA", SOLVER, r"\text{MDA}")

# Add fluid block
x.add_system("Fluid", FLUID, r"\text{Fluid}")

# Add solid block
x.add_system("Solid", SOLID, r"\text{Solid}")

# Add propulsion block
#x.add_system("Propulsion", PROPULSION, r"\text{Propulsion}")
#-------------------------DIAGONAL BLOCK DEFINITION:END--------------------------#

#-------------------------OFF-DIAGONAL BLOCK DEFINITION--------------------------#

# Add fluid sub-function
x.add_system("fluid_sub_func", FUNF, r"\text{traction()}")

# Add solid sub-function
x.add_system("solid_sub_func", FUNS, r"\text{displacement()}")


#-------------------------OFF-DIAGONAL BLOCK DEFINITION:END--------------------------#

# DEFINE CONECTIONS

# Fluid passes mesh coordinates x, y, z to traction()
x.connect("Fluid", "fluid_sub_func", r"\text{x,y,z}")


# Fluid sub func passes traction to solid
x.connect("fluid_sub_func", "Solid", r"f_x, f_y, f_z")

# Solid passes tractions to internal solver
x.connect("Solid", "solid_sub_func", r"f_x, f_y, f_z")

# Solid internal solver passes nodal displacements to fluid
x.connect("solid_sub_func", "Fluid", r"u_x, u_y, u_z")

# Solid passes elastic residual to MDA
x.connect("Solid", "MDA", r"\mathcal{S}")

# Fluid passes fluid residual to MDA
x.connect("Fluid", "MDA", r"\mathcal{F}")

# MDA passes aeroelastic residual to fluid for convergence check
x.connect("MDA", "Fluid", r"\mathcal{G}")

# MDA passes aeroelastic residual to solid for convergence check
x.connect("MDA", "Solid", r"\mathcal{G}")

x.write("mda")