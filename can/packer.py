# pylint: skip-file
import platform

if platform.python_implementation() == 'PyPy':
  from opendbc.can.packer_py  import CANPacker
else:
  from opendbc.can.packer_pyx import CANPacker
assert CANPacker
