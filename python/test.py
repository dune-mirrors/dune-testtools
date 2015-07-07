def comp(s):
    print "Trying with {}".format(s)
    try:
        return eval(s)
    except NameError as e:
        return comp(s.replace("x", "'x'"))

try:
    print comp("x == x")
except SyntaxError:
    raise SyntaxError("URGH!")
