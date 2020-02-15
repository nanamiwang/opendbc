import platform

if platform.python_implementation() == 'PyPy':
  from opendbc.can.parser_py  import CANParser
else:
  from opendbc.can.parser_pyx import CANParser # pylint: disable=no-name-in-module, import-error
assert CANParser
