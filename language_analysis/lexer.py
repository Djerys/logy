import re


class Lexer(object):
    def __init__(self, token_patterns):
        self.token_patterns = token_patterns

    def __repr__(self):
        return f'Lexer: {self._token_patterns}'

    @property
    def token_patterns(self):
        return self._token_patterns

    @token_patterns.setter
    def token_patterns(self, value):
        if not self._is_token_patterns(value):
            raise ValueError(
                'Token patterns should be a container of pairs '
                'consisting of a string pattern and a tag.')
        self._token_patterns = value

    def __call__(self, characters):
        position = 0
        tokens = []

        while position < len(characters):
            for pattern, tag in self.token_patterns:
                match = re.compile(pattern).match(characters, position)
                if match:
                    term = match.group(0)
                    if tag is not None:
                        token = term, tag
                        tokens.append(token)
                    break
            else:
                raise ValueError(
                    f'Illegal character "{characters[position]}" '
                    'for contained token expressions!')
            position = match.end(0)

        return tokens

    def _is_token_patterns(self, checking):
        def is_token_pattern(checking_unit):
            return (len(checking_unit) == 2
                    and isinstance(checking_unit[0], str))

        return all([is_token_pattern(c) for c in checking])
