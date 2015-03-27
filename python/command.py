""" A module that defines commands that can be used from within a meta ini file

Arbitrary commands can be registered through the decorator meta_ini_command and
will be parsed and executed by the meta ini parser.

To implement a custom command you have to do the following:
- provide a function, that does what you want to do using only named arguments from the following list:
  * key : the key in the current line
  * value : the value string in the current line
  * TODO continue
- decorate it with @meta_ini_command. meta_ini_command itself takes some arguments:
  * name : How to use this command from a meta ini file
  * ctype : the command type, a.k.a. when to execute the command. defaults to CommandType.POST_RESOLUTION, which is after all curly brackets in the file have been resolved.
  * argc : the number of arguments that can be specified within the meta ini file.

Example:
@meta_ini_command(name="tolower")
def cmd_to_lower(value=None):
    return value.lower() if value else None

Allows you to write:
x = CAPS | tolower
in your meta inifile and have it resolved to:
x = caps
"""

_registry = {}

class CommandType:
    """ Define command types """
    POST_PARSE = 0
    PRE_EXPANSION = 1
    POST_EXPANSION = 2
    PRE_RESOLUTION = 3
    POST_RESOLUTION = 4

def meta_ini_command(**kwargs):
    """ A decorator for registered commands. """
    return lambda f: RegisteredCommand(f, **kwargs)

class RegisteredCommand:
    """ build the command object """
    def __init__(self, func, name=None, ctype=CommandType.POST_RESOLUTION, argc=0):
        # store the function to execute abd the command type
        self._func = func
        self._name = name
        self._ctype = ctype
        self._argc = argc

        if not name:
            raise ValueError("You have to provide a name argument when registering a custom command!")

        # register this instance in the registry
        _registry[name] = self

    def __repr__(self):
        return "Registered command {} - Function object <{}>".format(self._name, self._func)

    def __call__(self, **kwargs):
        # apply the original function by filtering all keyword arguments that it needs:
        return self._func(**{k : v for (k, v) in kwargs.items() if k in self._func.func_code.co_varnames})

@meta_ini_command(name="tolower")
def cmd_to_lower(value=None):
    return value.lower() if value else None

# TODO implement a generic command parser
