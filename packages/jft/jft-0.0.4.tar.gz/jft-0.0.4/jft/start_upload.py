from os import system
from jft.fake.os.system import f as fake_system

f = lambda sys=system: sys('twine upload dist/*')

def t():
  fake_sys = fake_system()
  f(fake_sys)
  return fake_sys.history == ['twine upload dist/*']
