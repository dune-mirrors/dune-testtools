.. _introductionmetaini:

Introduction to Meta Ini Files
******************************

The Meta Ini Format
===================

The *meta ini* format is used in dune-testtools as a domain specific language for feature modelling. It is an extension to the ini format as used in DUNE. To reiterate the syntax of such ini file, see the :ref:`normal_ebnf` and :ref:`normalini`. Note that, you can define groups of keys either by using the ``[..]`` syntax, by putting dots into keys, or by using a combination of both

.. _normal_ebnf:
.. code-block:: ebnf
   :caption: EBNF describing normal DUNE-style ini files

    <ini>    ::= {<pair> | <group>}*
    <group>  ::= [ <str> ]
    <pair>   ::= <str> = <str>

.. _normalini:
.. code-block:: ini
   :caption: A normal DUNE-style ini file

    key = value
    somegroup.x = 1
    [somegroup]
    y = 2
    [somegroup.subgroup]
    z = 3

The meta ini format is an extension to the normal ini file, which describes a set of ini files within one file. This is the EBNF of the extended syntax:

.. _metaini_ebnf:
.. code-block:: ebnf
   :caption: EBNF describing normal meta ini files

    <ini> & ::= {<pair> | <group> | <include> }*
    <group> & ::= [ <str> ]
    <pair> & ::= <str> = <value>{ | <command>}*
    <value> & ::= <str>{ { <value> } }*<str>
    <command> & ::= <cmdname> {<cmdargs>}*
    <include> & ::= include <str> | import <str>

The following sections are about describing the semantics of the extensions.

The command syntax
==================

Commands can be applied to key/value pairs by using a pipe and then stating the command name and potential arguments. As you'd expect from a pipe, you can use multiple commands on single key/value pair. If so, the order of resolution is the following

 - Commands with a command type of higher priority are executed first. The available command types in order of priority are: ``POST_PARSE``, ``PRE_EXPANSION``, ``POST_EXPANSION``, ``PRE_RESOLUTION``, ``POST_RESOLUTION``, ``PRE_FILTERING``, ``POST_FILTERING``, ``AT_EXPANSION``.
 - Given multiple commands with the same type, commands are executed from left to right.


The expand command
==================

The ``expand`` command is the most important command, as it defines the mechanism to provide sets of ini files. The values of keys that have the expand command are expected to be comma-separated lists. That list is split and the set of configurations is updated to hold the product of all possibile values. The example shows a simple example which yields 6 ini files.

.. code-block:: ini
   :caption: A simple example of expanded keys

    key = foo, bar | expand
    someother = 1, 2, 3 | expand

Sometimes, you may not want to generate the product of possible values, but instead couple multiple key expansions. You can do that by providing an argument to the expand command. All expand commands with the same argument, will be expanded together. Having expand commands with the same argument but a differing number of camma separated values is not well-defined. This example shows again a minimal example, which yields 2 configurations.

.. code-block:: ini
   :caption: A simple example of expanded keys with argument

    key = 1, 2 | expand foo
    someother = 4, 5 | expand foo

The above mechanism can be combined at will. Listing~\ref{lst:exp3} shows an example, which yields 6 ini files.

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

The following subsections describes all other general purpose commands, that exist in dune-testtools. This does not cover commands that are specific to certain testtools. Those are described in the section :ref:`thewrappers`.

The unique command
++++++++++++++++++

A key marked with the command ``unique`` will be made unique throughout the set of generated ini files. This is done by appending a consecutive numbering scheme to those (and only those) values, that appear multiple times in the set. Some special keys like ``__name`` have the unique command applied automatically.

Using the curly bracket syntax to depend on keys which have the ``unique`` command applied is not well-defined.

Simple value-altering commands: tolower, toupper, eval
++++++++++++++++++++++++++++++++++++++++++++++++++++++

``tolower`` is a command turning the given value to lowercase. ``toupper`` converts to uppercase respectively.

The ``eval`` command applies a simple expression parsing to the given value. The following operators are recognized
- addition (``+``)
- subtraction (``-``)
- multiplication (``*``)
- floating point division (``/``)
- a power function(``^``)
- unary minus (``-``).

Operands may be any literals, ``pi`` is expanded to its value.

.. code-block:: ini
   :caption: An example of the eval command

    radius = 1, 2, 3 | expand
    circumference = 2 * {r} * pi | eval

.. note::
    The ``eval`` command is currently within the ``POST_FILTERING`` priority group. That means you cannot have other values depend on the result with the curly bracket syntax.

The include statement
+++++++++++++++++++++

The ``include`` statement can be used to paste the contents of another inifile into the current ini file. The positioning of the statement within the ini file defines the priority order of keys that appear on both files. All keys prior to the include statements are potentially overriden if they appear in the include. Likewise, all keys after the include will override those from the include file with the same name.

This command is not formulated as a command, because it does, by definition not operate on a key/value pair. For convenience, ``include`` and ``import`` are synonymous w.r.t. to this feature.

Escaping in meta ini files
++++++++++++++++++++++++++

Meta ini files contain some special characters. Those are:

- ``[`` and ``]``	in group declarations
- ``=``		        in key/value pairs
- ``{`` and ``}``	in values for key-dependent resolution
- ``|``		        in values for piping commands
- ``,``		        in comma separated value lists when using the ``expand`` command

All those character can be escaped with a preceding backslash. It is currently not possible to escape a backslash itself. It is neither possible to use quotes as a mean of escaping instead. Escaping is only necessary when the character would have special meaning (You could in theory have for example commata in keys). Escaping a dot in a groupname is currently not supported, but it would be bad style anyway.
