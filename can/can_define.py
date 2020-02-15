import platform

if platform.python_implementation() == 'PyPy':
  from opendbc.can.can_define_py  import CANDefine
else:
  from opendbc.can.parser_pyx import CANDefine # pylint: disable=no-name-in-module, import-error
assert CANDefine
