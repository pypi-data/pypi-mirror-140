f = lambda a, b: a==b
t = lambda: all([
  f(0,0),
  f(1,1),
  f('a','a'),
  f(-1,-1),
  not f(0,1),
  not f(1,0),
  not f('a','b'),
  not f(-1,1)
])