Γ = [
  'def f(',
  'def f():',
  'def f(x):',
  'def f(a, b):',
  'f = lambda a, b:',
  'f = lambda x:',
  'f = lambda:',
  'f = lambda',
]

f = lambda x: any([λ.startswith(γ) for γ in Γ for λ in x.split('\n')])

t = lambda: all([
  # Expecation == Observation
  f("f = lambda x:"),
  f("f = lambda x:\nt = lambda:"),
  not f("t = lambda:"),
  not f(""),
])
