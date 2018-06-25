from pyxdsm.XDSM import XDSM

#
opt = 'Optimization'
solver = 'MDA'
comp = 'Analysis'
group = 'Metamodel'
func = 'Function'

x = XDSM()

x.add_system('opt', opt, r'\text{Optimizer}')
x.add_system('solver', solver, r'\text{Newton}')
x.add_system('D1', comp, r'D_1')
x.add_system('D2', comp, r'D_2')
x.add_system('F', func, r'F')
x.add_system('G', func, r'G')


x.connect('opt', 'D1', r'x, z')
x.connect('opt', 'D2', r'z')
x.connect('opt', 'F', r'x, z')
x.connect('solver', 'D1', r'y_2')
x.connect('solver', 'D2', r'y_1')
x.connect('D1', 'solver', r'\mathcal{R}(y_1)')
x.connect('solver', 'F', r'y_1, y_2')
x.connect('D2', 'solver', r'\mathcal{R}(y_2)')
x.connect('solver', 'G', r'y_1, y_2')


x.connect('F', 'opt', r'f')
x.connect('G', 'opt', r'g')

x.add_output('opt', r'x^*, z^*', side='left')
x.add_output('D1', r'y_1^*', side='left')
x.add_output('D2', r'y_2^*', side='left')
x.add_output('F', r'f^*', side='left')
x.add_output('G', r'g^*', side='left')
x.write('mdf')
