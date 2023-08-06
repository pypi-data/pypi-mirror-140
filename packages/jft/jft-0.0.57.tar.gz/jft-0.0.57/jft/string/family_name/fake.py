from jft.file.load import f as load
from json import loads 
from random import choice
from jft.dict.frequencies.choose import f as choose
from jft.string.given_name.is_a import f as is_a_given_name

def f():
  root = './jft/string/family_name'
  q3_json = load(f'{root}/q3.json')
  q3 = loads(q3_json)
  q3_keys = sorted(list(q3.keys()))
  q3_keys_where_first_char_in_AZ = q3_keys[:q3_keys.index('aa')]
  _z = choice(q3_keys_where_first_char_in_AZ)
  _2 = q3[_z[-2:]]
  while _2 != '!':
    _2 = choose(q3[_z[-2:]])
    _z += _2
  return _z[:-1]

t = lambda: is_a_given_name(f())