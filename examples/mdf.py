from pyxdsm.XDSM import XDSM

#
opt = 'Optimization'
solver = 'MDA'
func = 'Function'

# Change `use_sfmath` to False to use computer modern
x = XDSM(use_sfmath=True)

x.add_system('opt', opt, r'\text{Optimizer}')
x.add_system('solver', solver, r'\text{Newton}')
x.add_system('D1', func, 'D_1')
x.add_system('D2', func, 'D_2')
x.add_system('F', func, 'F')
x.add_system('G', func, 'G')

x.connect('opt', 'D1', 'x, z')
x.connect('opt', 'D2', 'z')
x.connect('opt', 'F', 'x, z')
x.connect('solver', 'D1', 'y_2')
x.connect('solver', 'D2', 'y_1')
x.connect('D1', 'solver', r'\mathcal{R}(y_1)')
x.connect('solver', 'F', 'y_1, y_2')
x.connect('D2', 'solver', r'\mathcal{R}(y_2)')
x.connect('solver', 'G', 'y_1, y_2')

x.connect('F', 'opt', 'f')
x.connect('G', 'opt', 'g')

x.add_output('opt', 'x^*, z^*', side='left')
x.add_output('D1', 'y_1^*', side='left')
x.add_output('D2', 'y_2^*', side='left')
x.add_output('F', 'f^*', side='left')
x.add_output('G', 'g^*', side='left')
x.write('mdf')
