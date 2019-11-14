from language_analysis.lexer import Lexer


OPERATOR = 0
CONSTANT = 1
VARIABLE = 2


NOT = '-'
AND = '*'
NAND = '/'
OR = '+'
NOR = '!'
XOR = '^'
IMPLY = '->'
EQ = '<->'


token_patterns = [
    (r'[ \n\t]+', None),
    (r'\*', OPERATOR),
    (r'\+', OPERATOR),
    (r'\^', OPERATOR),
    (r'/', OPERATOR),
    (r'!', OPERATOR),
    (r'->', OPERATOR),
    (r'<->', OPERATOR),
    (r'-', OPERATOR),
    (r'\(', OPERATOR),
    (r'\)', OPERATOR),
    (r'[0-1]', CONSTANT),
    (r'[A-Za-z]', VARIABLE),
]

lex = Lexer(token_patterns)
