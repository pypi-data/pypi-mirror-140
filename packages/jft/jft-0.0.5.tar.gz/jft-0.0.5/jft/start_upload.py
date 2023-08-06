from os import system
from jft.fake.os.system import f as fake_system
from subprocess import run as sprun
from jft.fake.subprocess.run import f as fake_sprun
from jft.directory.make import f as mkdirine
from jft.directory.remove import f as rmdirie

_dir = '../start_upload'

def setup(): return mkdirine(_dir)
def tear_down(): return rmdirie(_dir)

def f(sprun, cwd='.', capture_output=True):
  return sprun(
    [
      'twine',
      'upload',
      'dist/*'
      '-u',
      'john.robert.forbes',
      '-p',
      'KESR!kK7WtQAZx@'
    ],
    cwd=cwd,
    capture_output=capture_output
  )

def t():
  setup()
  observation = f(fake_sprun, cwd=_dir)
  print(f'observation: {observation}')
  result = False
  tear_down()
  return result
