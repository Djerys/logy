from functools import reduce

import boolean_ast as ast
import boolean_lexer as blex
import language_analysis.combinators as cmb


def parse(tokens):
    return parser()(tokens, 0).tree


def parser():
    return cmb.Phrase(boolean())


def boolean():
    # return cmb.Phrase(
    #     precedence(term(), precedence_levels, binary_nodes))
    return precedence(term(), precedence_levels, binary_nodes)


def precedence(value_parser, precedence_levels, combine):
    def operator_parser(precedence_level):
        return any_operator(precedence_level) ^ combine

    parser = value_parser
    for precedence_level in precedence_levels:
        parser = parser * operator_parser(precedence_level)
    return parser


def binary_nodes(operator):
    if operator not in operator_nodes:
        raise RuntimeError(f'Unknown logic operator: {operator}')
    return lambda l, r: operator_nodes[operator](l, r)


def term():
    return boolean_not() | boolean_value() | boolean_group()


def boolean_value():
    return (constant ^ (lambda x: ast.ConstantExpression(x))
            | variable ^ (lambda x: ast.VariableExpression(x)))


def boolean_not():
    return (operator('-') + cmb.Lazy(term)
            ^ (lambda parsed: ast.NotExpression(parsed[1])))


def boolean_group():
    return operator('(') + cmb.Lazy(boolean) + operator(')') ^ ungroup


def operator(op):
    return cmb.Reserved(op, blex.OPERATOR)


def ungroup(parsed):
    ((_, exp), _) = parsed
    return exp


def any_operator(operators):
    operator_parsers = [operator(o) for o in operators]
    parser = reduce(lambda l, r: l | r, operator_parsers)
    return parser


constant = cmb.Tag(blex.CONSTANT) ^ (lambda x: int(x))
variable = cmb.Tag(blex.VARIABLE)


operator_nodes = {
    '&': ast.AndExpression,
    '/': ast.NandExpression,
    'V': ast.OrExpression,
    '>': ast.NorExpression,
    '^': ast.XorExpression,
    '->': ast.ImplyExpression,
    '<->': ast.EqExpression,
}


precedence_levels = [
    ['&', '/'],
    ['V', '>'],
    ['^', '->', '<->'],
]
