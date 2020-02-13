import platform
import os
from cffi import FFI

if platform.python_implementation() == 'PyPy':
  base_dir = os.path.dirname(os.path.abspath(__file__))
  libdbc_fn = os.path.join(base_dir, "libdbc.so")

  ffi = FFI()
  ffi.cdef("""

  typedef enum {
    DEFAULT,
    HONDA_CHECKSUM,
    HONDA_COUNTER,
    TOYOTA_CHECKSUM,
    PEDAL_CHECKSUM,
    PEDAL_COUNTER,
    VOLKSWAGEN_CHECKSUM,
    VOLKSWAGEN_COUNTER,
  }SignalType;

  typedef struct {
    const char* name;
    int b1, b2, bo;
    bool is_signed;
    double factor, offset;
    bool is_little_endian;
    SignalType type;
  }Signal;

  typedef struct {
    const char* name;
    uint32_t address;
    unsigned int size;
    size_t num_sigs;
    const Signal *sigs;
  }Msg;

  typedef struct {
    const char* name;
    uint32_t address;
    const char* def_val;
    const Signal *sigs;
  }Val;

  typedef struct {
    const char* name;
    size_t num_msgs;
    const Msg *msgs;
    const Val *vals;
    size_t num_vals;
  }DBC;

  const DBC* dbc_lookup(const char* dbc_name);
  """)

  libdbc_ffi = ffi.dlopen(libdbc_fn)


  class CANDefine:
    def __init__(self, dbc_name):
      self.dbc_name = dbc_name
      self.dbc = libdbc_ffi.dbc_lookup(dbc_name)


else:
  from opendbc.can.parser_pyx import CANDefine # pylint: disable=no-name-in-module, import-error
assert CANDefine
