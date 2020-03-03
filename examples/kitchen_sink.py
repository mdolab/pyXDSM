from pyxdsm.XDSM import XDSM

# styling names for the boxes
opt = 'Optimization'
subopt = 'SubOptimization'
solver = 'MDA'
doe = 'DOE'
ifunc = 'ImplicitFunction'
func = 'Function'
group = 'Group'
igroup = 'ImplicitGroup'
metamodel = 'Metamodel'

x = XDSM()

x.add_system('opt', opt, r'\text{Optimizer}')
x.add_system('DOE', doe, r'\text{DOE}')
x.add_system('MDA', solver, r'\text{Newton}')
x.add_system('D1', func, 'D_1')

# can fade out blocks to allow for emphasis on sub-sections of XDSM
x.add_system('D2', ifunc, 'D_2', faded=True)

x.add_system('D3', ifunc, 'D_3')
x.add_system('subopt', subopt, 'SubOpt')
x.add_system('G1', group, 'G_1')
x.add_system('G2', igroup, 'G_2')
x.add_system('MM', metamodel, 'MM')

# if you give the label as a list or tuple, it splits it onto multiple lines
x.add_system('F', func, ('F', r'\text{Functional}'))

# stacked can be used to represent multiple instances that can be run in parallel
x.add_system('H', func, 'H', stack=True)

x.add_process(['opt', 'DOE', 'MDA', 'D1', 'D2', 'subopt', 'G1', 'G2', 'MM', 'F', 'H', 'opt'], arrow=True)

x.connect('opt', 'D1', ['x', 'z', 'y_2'], label_width=2)
x.connect('opt', 'D2', 'z, y_1')
x.connect('opt', 'D3', 'z, y_1')
x.connect('opt', 'subopt', 'z, y_1')
x.connect('subopt', 'G1', 'z_2')
x.connect('subopt', 'G2', 'z_2')
x.connect('subopt', 'MM', 'z_2')
x.connect('opt', 'G2', 'z')
x.connect('opt', 'F', 'x, z')
x.connect('opt', 'F', 'y_1, y_2')

# you can also stack variables
x.connect('opt', 'H', 'y_1, y_2', stack=True)

x.connect('D1', 'opt', r'\mathcal{R}(y_1)')
x.connect('D2', 'opt', r'\mathcal{R}(y_2)')

x.connect('F', 'opt', 'f')
x.connect('H', 'opt', 'h', stack=True)

# can specify inputs to represent external information coming into the XDSM
x.add_input('D1', 'P_1')
x.add_input('D2', 'P_2')
x.add_input('opt', r'x_0', stack=True)

# can put outputs on the left or right sides
x.add_output('opt', r'x^*, z^*', side='right')
x.add_output('D1', r'y_1^*', side='left')
x.add_output('D2', r'y_2^*', side='left')
x.add_output('F', r'f^*', side='right')
x.add_output('H', r'h^*', side='right')
x.add_output('opt', r'y^*', side='left')

x.add_process(['output_opt', 'opt', 'left_output_opt'])

x.write('kitchen_sink', cleanup=False)
