""" A meta ini command extension for Sphinx"""

from docutils import nodes
from docutils.parsers.rst import Directive
from itertools import chain


class MetaIniArgNode(nodes.Element):
    pass


class MetaIniCommand(Directive):
    # We do require the name to be an argument
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {'operates_on_value' : lambda s: True}
    has_content = True

    def run(self):
        env = self.state.document.settings.env

        # Parse the content of the directive recursively
        node = nodes.Element()
        node.document = self.state.document
        self.state.nested_parse(self.content, self.content_offset, node)

        # define defaults
        node['name'] = self.arguments[0]
        node['operates_on_value'] = self.options.get('operates_on_value', False)
        node['content'] = self.content

        arg_nodes = []
        other_nodes = []
        required_params = {}
        optional_params = {}

        for child in node:
            if isinstance(child, MetaIniArgNode):
                if child["required"]:
                    required_params[child["name"]] = child
                else:
                    optional_params[child["name"]] = child
            else:
                other_nodes.append(child)


        # Build the content of the box
        prefix = ''
        if node["operates_on_value"]:
            prefix = '<value> | '
        else:
            prefix = '<key> = <value> | '

        sl = [prefix + self.arguments[0]+ ' ']

        for rp, paramnode in required_params.items():
            if paramnode["multi"]:
                sl.append('<' + paramnode['name'] + '1 [' + paramnode['name'] + '2 ...]' + '> ')
            if paramnode["single"]:
                sl.append('<' + paramnode['name'] + '> ')

        for op, paramnode in optional_params.items():
            if paramnode["multi"]:
                sl.append('[<' + paramnode['name'] + '1 [' + paramnode['name'] + '2 ...]' + '>] ')
            if paramnode["single"]:
                sl.append('[<' + paramnode['name'] + '>] ')

        lb = nodes.literal_block(''.join(sl), ''.join(sl))
        arg_nodes.append(lb)

        # provide a defition list for the arguments
        dl = nodes.definition_list()
        for param, paramnode in chain(required_params.items(), optional_params.items()):
            dli = nodes.definition_list_item()
            dl += dli

            dlit = nodes.term(text=param)
            dli += dlit

            dlic = nodes.definition()
            dli += dlic
            self.state.nested_parse(paramnode['content'], self.content_offset, dlic)

        # add the parameter list to the output
        arg_nodes.append(dl)

        # Add a target for referencing!
        section = nodes.section(names=[node['name']])
        section += nodes.subtitle(text="The " + node['name'] + " command")

        return [section] + arg_nodes + other_nodes


class MetaIniCommandArg(Directive):
    # We do require the name to be an argument
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {'argname' : lambda s: s,
                   'multi': lambda s: True,
                   'required': lambda s: True,
                   'single': lambda s: True
                   }
    has_content = True

    def run(self):
        node = MetaIniArgNode()
        # set defaults:
        node['name'] = self.arguments[0]
        node['single'] = self.options.get('single', False)
        node['multi'] = self.options.get('multi', False)
        node['required'] = self.options.get('required', False)
        node['content'] = self.content
        return [node]


def setup(app):
    app.add_node(MetaIniArgNode)
    app.add_directive('metaini_command', MetaIniCommand)
    app.add_directive('metaini_command_arg', MetaIniCommandArg)

    return {'version': '0.1'}
