from pyxdsm.XDSM import XDSM

# styling names for the boxes
opt = 'Optimization'
comp = 'Analysis'

x = XDSM()

# create a couple of nodes to connect
x.add_system('opt', opt, 'Optimizer')
x.add_system('D1', comp, r'$D_1$')

# create a process arrow to show directional data flow
x.add_process_arrow('opt', 'D1')

x.write('arrow', cleanup=False)
