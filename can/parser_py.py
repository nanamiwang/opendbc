import time
import numbers

from opendbc.can.libdbc_py import libdbc, ffi

CAN_INVALID_CNT = 5  # after so many consecutive CAN data with wrong checksum, counter or frequency, flag CAN invalidity

class CANParser(object):
  def __init__(self, dbc_name, signals, checks=None, bus=0):
    if checks is None:
      checks = []

    self.can_valid = True
    self.can_invalid_cnt = CAN_INVALID_CNT
    self.vl = {}
    self.ts = {}

    self.dbc_name = dbc_name
    self.dbc = libdbc.dbc_lookup(dbc_name.encode('ascii'))
    self.msg_name_to_addres = {}
    self.address_to_msg_name = {}

    num_msgs = self.dbc[0].num_msgs
    for i in range(num_msgs):
      msg = self.dbc[0].msgs[i]

      name = ffi.string(msg.name).decode('ascii')
      address = msg.address

      self.msg_name_to_addres[name] = address
      self.address_to_msg_name[address] = name

      self.vl[address] = {}
      self.vl[name] = {}
      self.ts[address] = {}
      self.ts[name] = {}

    # Convert message names into addresses
    for i in range(len(signals)):
      s = signals[i]
      if not isinstance(s[1], numbers.Number):
        s = (s[0], self.msg_name_to_addres[s[1]], s[2])
        signals[i] = s

    for i in range(len(checks)):
      c = checks[i]
      if not isinstance(c[0], numbers.Number):
        c = (self.msg_name_to_addres[c[0]], c[1])
        checks[i] = c

    sig_names = dict((name, ffi.new("char[]", name.encode('ascii'))) for name, _, _ in signals)

    signal_options_c = ffi.new("SignalParseOptions[]", [
      {
        'address': sig_address,
        'name': sig_names[sig_name],
        'default_value': sig_default,
      } for sig_name, sig_address, sig_default in signals])

    message_options = dict((address, 0) for _, address, _ in signals)
    message_options.update(dict(checks))

    message_options_c = ffi.new("MessageParseOptions[]", [
      {
        'address': msg_address,
        'check_frequency': freq,
      } for msg_address, freq in message_options.items()])

    self.can = libdbc.can_init(bus, dbc_name.encode('ascii'), len(message_options_c), message_options_c,
                               len(signal_options_c), signal_options_c)

    self.p_can_valid = ffi.new("bool*")

    value_count = libdbc.can_query(self.can, self.p_can_valid, 0, ffi.NULL)
    self.can_values = ffi.new("SignalValue[%d]" % value_count)
    self.update_vl()

  def update_vl(self):
    can_values_len = libdbc.can_query(self.can, self.p_can_valid, len(self.can_values), self.can_values)
    assert can_values_len <= len(self.can_values)

    self.can_invalid_cnt += 1
    if self.p_can_valid[0]:
      self.can_invalid_cnt = 0
    self.can_valid = self.can_invalid_cnt < CAN_INVALID_CNT

    ret = set()
    for i in range(can_values_len):
      cv = self.can_values[i]
      address = cv.address
      # print("{0} {1}".format(hex(cv.address), ffi.string(cv.name)))
      name = ffi.string(cv.name).decode('ascii')
      self.vl[address][name] = cv.value
      self.ts[address][name] = cv.ts

      sig_name = self.address_to_msg_name[address]
      self.vl[sig_name][name] = cv.value
      self.ts[sig_name][name] = cv.ts
      ret.add(address)
    return ret

  def update_string(self, dat, sendcan=False):
    libdbc.can_update_string(self.can, dat, len(dat), sendcan)
    return self.update_vl()

  def update_strings(self, strings, sendcan=False):
    updated_vals = set()

    for s in strings:
      updated_val = libdbc.can_update_string(self.can, s, len(s), sendcan)
      updated_vals.update(updated_val)

    return updated_vals
