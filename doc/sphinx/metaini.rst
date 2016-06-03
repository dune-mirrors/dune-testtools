.. _introductionmetaini:

Introduction to Meta Ini Files
******************************

The Meta Ini Format
===================

The *meta ini* format is used in dune-testtools as a domain specific language for feature modelling. It is an extension to the ini format as used in DUNE. To reiterate the syntax of such ini file, see the example :ref:`normalini`.
Note that, you can define groups of keys either by using the ``[..]`` syntax, by putting dots into keys, or by using a combination of both.

.. _normalini:
.. code-block:: ini
   :caption: A normal DUNE-style ini file

    key = value
    somegroup.x = 1
    [somegroup]
    y = 2
    [somegroup.subgroup]
    z = 3

The meta ini format is an extension to the normal ini file, which describes a set of ini files within one file.
The following sections are about describing the semantics of these extensions.

The command syntax
==================

dune-testoools defines a set of commands, which may be applied to key/value pairs by using a Unix-style pipe. A command may also take several arguments. As you'd expect from a pipe, you can use multiple commands on single key/value pair.
The most import command is ``expand`` and will be explained in much detail below.


The expand command
==================

The ``expand`` command is the most important command, as it defines the mechanism to provide sets of ini files. The values of keys that have the expand command are expected to be comma-separated lists. That list is split and the set of configurations is updated to hold the product of all possibile values. The example shows a simple example which yields 6 ini files.

.. code-block:: ini
   :caption: A simple example of expanded keys

    key = foo, bar | expand
    someother = 1, 2, 3 | expand

Sometimes, you may not want to generate the product of possible values, but instead couple multiple key expansions. You can do that by providing an argument to the expand command. All expand commands with the same argument will be expanded together. Having expand commands with the same argument but a differing number of camma separated values is not well-defined. This example shows again a minimal example, which yields 2 configurations.

.. code-block:: ini
   :caption: A simple example of expanded keys with argument

    key = 1, 2 | expand foo
    someother = 4, 5 | expand foo

The above mechanism can be combined at will. The following example yields 6 ini files.

.. code-block:: ini
   :caption: A simple combining multiple expansions

    key = foo, bar | expand 1
    someother = 1, 2, 3 | expand
    bla = 1, 2 | expand 1

Key-dependent values
++++++++++++++++++++

Whenever values that contain unescaped curly brackets, the string within those curly brackets will be interpreted as a key and will be replaced by the associated value (after expansion). This feature can be used as many times as you wish, even in a nested fashion, as long as no circular dependencies arise. In that example one configuration with ``y=1`` and one with ``y=2`` would be generated.

.. code-block:: ini
   :caption: A complex example of key-dependent value syntax

    k = a, ubb | expand
    y = {bl{k}}
    bla = 1
    blubb = 2

Other commands
==============

For the documentation of all other available commands, we refer to the documentation of the python package:

- :ref:`cmake_discard`
- :ref:`exclude`
- :ref:`eval`
- :ref:`label`
- :ref:`tolower`
- :ref:`toupper`

The include statement
+++++++++++++++++++++

The ``include`` statement can be used to paste the contents of another inifile into the current ini file. The positioning of the statement within the ini file defines the priority order of keys that appear on both files. All keys prior to the include statements are potentially overriden if they appear in the include. Likewise, all keys after the include will override those from the include file with the same name.

This command is not formulated as a command, because it does, by definition not operate on a key/value pair. For convenience, ``include`` and ``import`` are synonymous w.r.t. to this feature.

Escaping in meta ini files
==========================

Meta ini files contain some special characters. Those are:

- ``[`` and ``]``	in group declarations
- ``=``		        in key/value pairs
- ``{`` and ``}``	in values for key-dependent resolution
- ``|``		        in values for piping commands
- ``,``		        in comma separated value lists when using the ``expand`` command

You have two possibilities of escaping these:
- through a preceding backslash
- using double quotes

Priority of command application
===============================
When several commands are applied to the same key value pair, the order depends on the commands *execution point*.
The currently implemented execution points are:
- ``POST_PARSE``
- ``PRE_EXPANSION``
- ``AT_EXPANSION``
- ``POST_EXPANSION``
- ``PRE_RESOLUTION``
- ``POST_RESOLUTION``
- ``PRE_FILTERING``
- ``POST_FILTERING``
Typically, a command's execution point is the latest point, where its application is still semantically well-defined.

Given multiple commands with the same execution point, commands are executed from left to right.