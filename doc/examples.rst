.. _pyXDSM_examples:

Examples
========
Here is a simple example. 
There are some other more advanced things you can do as well. 
Check out the `examples folder <https://github.com/mdolab/pyXDSM/blob/master/examples>`_ for more complex scripts.

.. code-block:: python

    from pyxdsm.XDSM import XDSM, OPT, SOLVER, FUNC

    x = XDSM()

    x.add_system('opt', OPT, r'\text{Optimizer}')
    x.add_system('solver', SOLVER, r'\text{Newton}')
    x.add_system('D1', FUNC, 'D_1')
    x.add_system('D2', FUNC, 'D_2')
    x.add_system('F', FUNC, 'F')
    x.add_system('G', FUNC, 'G')

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


This will output ``mdf.tex``, a standalone tex document that (by default) is also compiled to ``mdf.pdf``, shown below:

.. image:: images/mdf.png
   :scale: 30


More complicated example
------------------------

Here is an example that uses a whole bunch of the more advanced features in ``pyXDSM``. 

.. image:: images/kitchen_sink.png
   :scale: 30

It is mostly just a reference for all the customizations you can do.
The code for this diagram is `provided here <https://github.com/mdolab/pyXDSM/blob/master/examples/kitchen_sink.py>`_