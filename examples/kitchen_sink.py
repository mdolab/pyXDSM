from pyxdsm.XDSM import XDSM

# styling names for the boxes
opt = 'Optimization'
solver = 'MDA'
ifunc = 'ImplicitFunction'
func = 'Function'

x = XDSM()

x.add_system('opt', opt, r'\text{Optimizer}')
x.add_system('D1', func, 'D_1')

# can fade out blocks to allow for emphasis on sub-sections of XDSM
x.add_system('D2', ifunc, 'D_2', faded=True)

x.add_system('D3', ifunc, 'D_3')

# if you give the label as a list or tuple, it splits it onto multiple lines
x.add_system('F', func, ('F', r'\text{Functional}'))

# stacked can be used to represent multiple instances that can be run in parallel
x.add_system('G', func, 'G', stack=True)

x.add_process(['opt', 'D1', 'D2', 'F', 'G', 'opt'], arrow=True)

x.connect('opt', 'D1', 'x, z, y_2')
x.connect('opt', 'D2', 'z, y_1')
x.connect('opt', 'D3', 'z, y_1')
x.connect('opt', 'F', 'x, z')
x.connect('opt', 'F', 'y_1, y_2')

# you can also stack variables
x.connect('opt', 'G', 'y_1, y_2', stack=True)

x.connect('D1', 'opt', r'\mathcal{R}(y_1)')
x.connect('D2', 'opt', r'\mathcal{R}(y_2)')

x.connect('F', 'opt', 'f')
x.connect('G', 'opt', 'g', stack=True)

# can specify inputs to represent external information coming into the XDSM
x.add_input('D1', 'P_1')
x.add_input('D2', 'P_2')

# can put outputs on the left or right sides
x.add_output('opt', r'x^*, z^*', side='right')
x.add_output('D1', r'y_1^*', side='left')
x.add_output('D2', r'y_2^*', side='left')
x.add_output('F', r'f^*', side='right')
x.add_output('G', r'g^*', side='right')

x.write('kitchen_sink', cleanup=False)
