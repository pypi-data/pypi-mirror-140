from string import ascii_uppercase
f = lambda x: all([isinstance(x, str), ' ' not in x, x[0] in ascii_uppercase])
t = lambda: all([f('Forbes'), not f('New York'), not f('apple')])
