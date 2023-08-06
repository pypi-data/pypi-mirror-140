from collections import namedtuple
def Flags(argv):
  obj = namedtuple("obj",["flag","arg","args"])
  args = argv[1:]
  flag = ""
  arg = ""
  argz = []
  if args != []:
    flag = args[0]
    if len(args) > 1:
      arg = args[1]
      if len(args) > 2:
        argz = args[2:]
  return obj(flag,arg,argz)
  