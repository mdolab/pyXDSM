from pyxdsm.matrix_eqn import MatrixEquation

################################
# define the system
################################

lin_system = MatrixEquation()

lin_system.add_variable(1, size=1, text="a")
lin_system.add_variable(2, size=1, text="b")

lin_system.add_variable(3, size=1, text="c")
lin_system.add_variable(4, size=2)
lin_system.add_variable(5, size=2)

lin_system.add_variable(6, size=1, text="d")
lin_system.add_variable(7, size=2)
lin_system.add_variable(8, size=2)

lin_system.add_variable(9, size=1, text="e")
lin_system.add_variable(10, size=2)
lin_system.add_variable(11, size=2)

# variable identifiers can be any hashable object
lin_system.add_variable("f", size=1, text="f")

lin_system.connect(1, [4, 5, 7, 8, 10, 11])
lin_system.connect(2, [4, 5, 7, 8, 10, 11])

lin_system.connect(3, 4)
lin_system.connect(4, 5)
lin_system.connect(5, 4)

lin_system.connect(6, 7)
lin_system.connect(7, 8)
lin_system.connect(8, 7)

lin_system.connect(9, 10)
lin_system.connect(10, 11)
lin_system.connect(11, 10)

lin_system.connect(11, "f")

################################
# setup the equation
################################
lin_system.jacobian()
lin_system.spacer()
lin_system.vector(base_color="red", highlight=[0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0])
lin_system.spacer()
lin_system.vector(base_color="red", highlight=[0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0])
lin_system.spacer()
lin_system.vector(base_color="red", highlight=[0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2])
lin_system.spacer()
lin_system.operator("=")
lin_system.vector(base_color="green", highlight=[1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1])
lin_system.spacer()
lin_system.vector(base_color="green", highlight=[1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1])
lin_system.spacer()
lin_system.vector(base_color="green", highlight=[1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1])
lin_system.spacer()

lin_system.write("mat_eqn_example")
