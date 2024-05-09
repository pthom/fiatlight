# This works, but is cumbersome
# import a
# cc = a.c.C()

# This does not work, but is closer to what I would like
# from a.c import C
# c = C()

# This works and is the better solution
from a.b import c as c

cc = c.C()
