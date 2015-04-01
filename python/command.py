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

from escapes import escaped_split

_registry = {}

class CommandType:
    """ Define command types """
    POST_PARSE = 0
    PRE_EXPANSION = 1
    POST_EXPANSION = 2
    PRE_RESOLUTION = 3
    POST_RESOLUTION = 4
    PRE_FILTERING = 5
    POST_FILTERING = 6
    AT_EXPANSION = 7

def meta_ini_command(**kwargs):
    """ A decorator for registered commands. """
    return lambda f: RegisteredCommand(f, **kwargs)

class RegisteredCommand:
    """ build the command object """
    def __init__(self, func, name=None, ctype=CommandType.POST_RESOLUTION, argc=0, returnValue=True):
        # store the function to execute abd the command type
        self._func = func
        self._name = name
        self._ctype = ctype
        self._argc = argc
        self._returnValue = returnValue

        if not name:
            raise ValueError("You have to provide a name argument when registering a custom command!")

        # register this instance in the registry
        _registry[name] = self

    def __repr__(self):
        return "Registered command {} - Function object <{}>".format(self._name, self._func)

    def __call__(self, **kwargs):
        # apply the original function by filtering all keyword arguments that it needs:
        ret = self._func(**{k : v for (k, v) in kwargs.items() if k in self._func.func_code.co_varnames})
        if self._returnValue:
            # update the configuration with the return value
            kwargs["config"][kwargs["key"]] = ret + kwargs["pipecommands"]
            # and process all piped commands of the same command type recursively
            if kwargs["pipecommands"] != "":
                apply_generic_command(config=kwargs["config"], key=kwargs["key"], ctype=kwargs["ctype"])

def apply_generic_command(config=None, key=None, ctype=CommandType.POST_RESOLUTION, **kwargs):
    """ inspect the given key for a command to apply and do so if present.
        This command returns the return value of the function or None if nothing has been done.
    """
    # split the value at the pipe symbol
    parts = escaped_split(config[key], delimiter="|", maxsplit=2)
    # first determine whether this is no op, because no |-operator is present
    if len(parts) is 1:
        return
    # Now investigate the given command.
    cmdargs = escaped_split(parts[1])
    # the first argument must be a valid command
    assert(cmdargs[0] in _registry)
    assert(len(cmdargs) <= _registry[cmdargs[0]]._argc + 1)
    # if the command type does not match our current command type, we are also no-op
    if ctype != _registry[cmdargs[0]]._ctype:
        return
    # Remove the command from the value!
    if ctype != CommandType.AT_EXPANSION:
        config[key] = parts[0]
    # call the actual function!
    _registry[cmdargs[0]](config=config, key=key, value=parts[0], args=cmdargs[1:], pipecommands=" | " + parts[2] if len(parts) == 3 else "", ctype=ctype, **kwargs)

@meta_ini_command(name="tolower")
def cmd_to_lower(value=None):
    return value.lower() if value else None

@meta_ini_command(name="toupper")
def cmd_to_upper(value=None):
    return value.upper() if value else None

@meta_ini_command(name="eval")
def _eval_command(value=None):
    import ast
    return str(ast.literal_eval(value))