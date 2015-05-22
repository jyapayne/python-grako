from __future__ import print_function, division, absolute_import, unicode_literals
from grako.parsing import graken, Parser
from grako.buffering import Buffer, PosLine, LineInfo
from grako.util import re, RE_FLAGS


__version__ = (2015, 5, 20, 15, 52, 20, 2)

from parser_class import PythonParser

class MyBuffer(Buffer):
    def __init__(
            self,
            text,
            filename=None,
            comments_re=None,
            eol_comments_re=None,
            whitespace=None,
            **kwargs):
        self.last_line = 0
        self.indent_stack = []
        super(MyBuffer, self).__init__(
            text,
            filename=filename,
            memoize_lookaheads=False,
            comment_recovery=True,
            comments_re=comments_re,
            whitespace=whitespace or '\t \f',
            eol_comments_re=eol_comments_re,
            **kwargs
        )

    def _dedent_from_stack(self, new_lines):
        while self.indent_stack:
            self.indent_stack.pop()
            new_lines[-1] +='<DEDENT>'
        return new_lines

    def process_leading_spaces(self, line, leading_spaces):
        if self.indent_stack:
            if len(leading_spaces) > len(self.indent_stack[-1]):
                line = '<INDENT>'+line
                self.indent_stack.append(leading_spaces)
            elif len(leading_spaces) < len(self.indent_stack[-1]):
                line = line+'<DEDENT>'
                self.indent_stack.pop()
        else:
            line = '<INDENT>'+line
            self.indent_stack.append(leading_spaces)
        return line

    def dedent_and_end(self, new_lines):
        new_lines = self._dedent_from_stack(new_lines)
        new_lines[-1] += '<EOF>'

    def indent_and_dedent_lines(self, lines):
        new_lines = []
        for line in lines:
            leading_spaces = re.search(u'^['+self.whitespace+']+', line)
            if leading_spaces is not None:
                leading_spaces = leading_spaces.group().strip('\n')
                if leading_spaces:
                    line = self.process_leading_spaces(line, leading_spaces)
                else:
                    new_lines = self._dedent_from_stack(new_lines)
            else:
                new_lines = self._dedent_from_stack(new_lines)

            new_lines.append(line)
        return new_lines

    def process_lines(self, lines):
        new_lines = self.indent_and_dedent_lines(lines)
        self.dedent_and_end(new_lines)
        return new_lines

    def process_block(self, name, lines, index, **kwargs):
        new_lines = self.process_lines(lines)
        return new_lines, index


def main(filename, startrule, trace=False, whitespace=None, nameguard=None):
    import json
    with open(filename) as f:
        text = f.read()
    parser = PythonParser(parseinfo=False)
    buf = MyBuffer(text, whitespace=whitespace,nameguard=nameguard,trace=trace,filename=filename)
    ast = parser.parse(
        buf,
        startrule,
        filename=filename,
        trace=trace,
        whitespace=whitespace,
        nameguard=nameguard)
    print('AST:')
    print(ast)
    print()
    print('JSON:')
    print(json.dumps(ast, indent=2))
    print()

if __name__ == '__main__':
    import argparse
    import string
    import sys

    class ListRules(argparse.Action):
        def __call__(self, parser, namespace, values, option_string):
            print('Rules:')
            for r in pythonParser.rule_list():
                print(r)
            print()
            sys.exit(0)

    parser = argparse.ArgumentParser(description="Simple parser for python.")
    parser.add_argument('-l', '--list', action=ListRules, nargs=0,
                        help="list all rules and exit")
    parser.add_argument('-n', '--no-nameguard', action='store_true',
                        dest='no_nameguard',
                        help="disable the 'nameguard' feature")
    parser.add_argument('-t', '--trace', action='store_true',
                        help="output trace information")
    parser.add_argument('-w', '--whitespace', type=str, default=None,
                        help="whitespace specification")
    parser.add_argument('file', metavar="FILE", help="the input file to parse")
    parser.add_argument('startrule', metavar="STARTRULE",
                        help="the start rule for parsing")
    args = parser.parse_args()

    main(
        args.file,
        args.startrule,
        trace=args.trace,
        whitespace=args.whitespace,
        nameguard=not args.no_nameguard
    )
