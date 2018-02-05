""" A module that defines the general infrastructure for commands that may be applied in meta ini files.

.. currentmodule:: dune.testtools.command_infrastructure

Arbitrary commands can be registered through the decorator meta_ini_command and
will be parsed and executed by the meta ini parser.

To implement a custom command you have to do the following:

1. provide a function, that does what you want to do using only named arguments from the following list:

    * key : the key in the current line
    * value : the value string in the current line
    * config : The configuration dictionary
    * configs : The list of all configurations
    * args : The list of arguments given to the command
    * argdefaults : A list of default arguments to apply, if the arguments are missing in the meta ini file.

2. decorate it with @ :func:`meta_ini_command`. :func:`meta_ini_command` itself takes some arguments:

    * name : How to use this command from a meta ini file (mandatory)
    * ctype : the command type, a.k.a. when to execute the command. defaults to CommandType.POST_RESOLUTION, which is after all curly brackets in the file have been resolved.
    * argc : the number of arguments that can be specified within the meta ini file.
    * returnValue : Whether a value is returned, which should be written into the given key.
    * returnConfigurations : Whether a list of configurations is returned, which should be replace the current list of configurations

Example:

.. code-block:: python

    @meta_ini_command(name="tolower")
    def cmd_to_lower(value=None):
        return value.lower() if value else None

Allows you to write:

.. code-block:: ini

    x = CAPS | tolower

in your meta inifile and have it resolved to:

.. code-block:: ini

    x = caps

"""

from __future__ import absolute_import
from dune.testtools.escapes import escaped_split, replace_delimited

_registry = {}


def command_registry():
    """ Get the registry of all registered, i.e. globally available commands."""
    return _registry


class CommandType:
    """ Define the following command types:

        * PRE_EXPANSION
        * POST_EXPANSION
        * PRE_RESOLUTION
        * AT_RESOLUTION
        * POST_RESOLUTION
        * PRE_FILTERING
        * POST_FILTERING
        * AT_EXPANSION
    """
    PRE_EXPANSION = 0
    POST_EXPANSION = 1
    PRE_RESOLUTION = 2
    AT_RESOLUTION = 3
    POST_RESOLUTION = 4
    PRE_FILTERING = 5
    POST_FILTERING = 6
    AT_EXPANSION = 7


def command_count():
    """ Return the total number of registered commands. """
    return max(v for v in list(CommandType.__dict__.values()) if type(v) == int) + 1


def meta_ini_command(**kwargs):
    """ A decorator for registered commands. """
    return lambda f: RegisteredCommand(f, **kwargs)


class RegisteredCommand:
    """ The registered command class """
    def __init__(self, func, name=None, ctype=CommandType.POST_RESOLUTION, argc=0, argdefaults=None, returnValue=True, returnConfigs=False):
        """ Build the registered command object """
        # store the function to execute abd the command type
        self._func = func
        self._name = name
        self._ctype = ctype
        self._argc = argc
        if argdefaults:
            self._argdefaults = list(argdefaults) + [None for i in range(argc - len(argdefaults))]
        else:
            self._argdefaults = list(None for x in range(argc))
        self._returnConfigs = returnConfigs
        # We cannot return both configurations and a value. Disable the returning of values if configurations are enabled
        if returnConfigs:
            returnValue = False
        self._returnValue = returnValue

        if not name:
            raise ValueError("You have to provide a name argument when registering a custom command!")
        if argdefaults and len(argdefaults) != argc:
            raise ValueError("Number of default arguments is not matching (use None for no default)")

        # register this instance in the registry
        _registry[name] = self

    def __repr__(self):
        """ Pretty representation of object of type :class:`RegisteredCommand` """
        return "Registered command {} - Function object <{}>".format(self._name, self._func)

    def __call__(self, **kwargs):
        """ Function style call """
        # apply default arguments to the given arguments
        kwargs["args"] = kwargs["args"] + [None for i in range(self._argc - len(kwargs["args"]))]
        kwargs["args"] = [a if kwargs["args"][i] is None else kwargs["args"][i] for i, a in enumerate(self._argdefaults)]

        # apply the original function by filtering all keyword arguments that it needs:
        return self._func(**{k: v for (k, v) in list(kwargs.items()) if k in self._func.__code__.co_varnames})


def apply_commands(configurations, cmds, all_cmds=[]):
    """Apply the given list of commands to a all configurations resulting from a meta ini expansion.

       :param configurations: The list of current configurations resulting from a meta ini expansion
       :type configurations: list
       :param cmds: The list of commands, as a list of named tuple CommandToApply. This information is extracted by the parser.
       :type cmds: list of CommandToApply
       :param all_cmds: The list of all CommandToApply retrieved by parsing the meta ini file.
       :type all_cmds: list of CommandToApply

    .. note::
        Application of a command might modify the list of all commands.
    """
    for cmd in cmds:
        # check whether the command ist still applicable. The key could have been filtered away!
        if cmd.key in configurations[0] or cmd.name == 'expand':
            if _registry[cmd.name]._returnConfigs:
                configurations[:] = _registry[cmd.name](args=cmd.args, key=cmd.key, configs=configurations, commands=all_cmds)
            else:
                for c in configurations:
                    replargs = [replace_delimited(arg, c, leftdelimiter="{", rightdelimiter="}") for arg in cmd.args]
                    ret = _registry[cmd.name](args=replargs, key=cmd.key, config=c, value=c[cmd.key], configs=configurations, commands=all_cmds)
                    if _registry[cmd.name]._returnValue:
                        c[cmd.key] = ret


def replace_command_key(commands, key, newkey):
    """Replace the key that a certain command is applied to

       :param commands: A list of commands
       :type commands: list
       :param key: The key whose value has a command attached. This key will be replaced by `newkey`
       :param newkey: The new key to replace the `key`

    """
    for cmdtype, cmdlist in list(commands.items()):
        for idx, cmd in list(enumerate(cmdlist)):
            if cmd.key == key:
                commands[cmdtype][idx] = cmd._replace(key=newkey)
