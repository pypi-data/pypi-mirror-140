from sfera.utils import concat, Dictionary


class Interpolator:

    default_start_token = '{'
    default_stop_token = '}'
    default_quotes = ["'", '"']
    default_string_escape = '\\'
    converters = Dictionary(
        a = ascii,
        r = repr,
        s = str,
    )

    def __init__(self, start_token=None, stop_token=None, quotes=None, string_escape=None):
        if start_token is None:
            start_token = self.default_start_token
        if stop_token is None:
            stop_token = self.default_stop_token
        if quotes is None:
            quotes = self.default_quotes
        if string_escape is None:
            string_escape = self.default_string_escape
        self.start_token = start_token
        self.stop_token = stop_token
        self.quotes = quotes
        self.string_escape = string_escape
        self._start_length = len(self.start_token)
        self._stop_length = len(self.stop_token)
    
    def __repr__(self):
        return f'interpolator {self.start_token}...{self.stop_token}'

    def interpolate(self, string, namespace):
        tokens = self.parse(string)
        return self.evaluate(tokens, namespace)
    
    def parse(self, string):
        if self.start_token not in string and self.stop_token not in string:
            return [(string, False)]
        tokens = []
        cursor = 0
        last_token = []
        while cursor < len(string):
            if string[cursor:cursor + self._start_length] == self.start_token:
                if string[cursor + self._start_length:cursor + 2*self._start_length] == self.start_token:
                    last_token.extend(self.start_token)
                    cursor += 2 * self._start_length
                else:
                    start = cursor + self._start_length
                    stop = self._skip_expression(start, string)
                    expression = string[start:stop].strip()
                    if last_token:
                        tokens.append((last_token, False))
                        last_token = []
                    tokens.append((expression, True))
                    stop += self._stop_length
                    cursor = stop
            elif string[cursor:cursor + self._stop_length] == self.stop_token:
                if string[cursor + self._stop_length:cursor + 2*self._stop_length] == self.stop_token:
                    last_token.extend(self.stop_token)
                    cursor += 2 * self._stop_length
                else:
                    raise ValueError(f'failed to parse {string!r}: unmatched {self.stop_token!r} at offset {cursor}')
            else:
                last_token.append(string[cursor])
                cursor += 1
        if last_token:
            tokens.append((last_token, False))
        output = []
        for token, is_expression in tokens:
            if not is_expression:
                token = ''.join(token)
            output.append((token, is_expression))
        return output
    
    def evaluate(self, tokens, namespace):
        output = []
        for token, is_expression in tokens:
            if is_expression:
                result = self._evaluate(token, namespace)
            else:
                result = token
            output.append(result)
        output = ''.join(output)
        return output
    
    def _skip_expression(self, cursor, string):
        depth = 1
        while cursor < len(string):
            if string[cursor:cursor + self._start_length] == self.start_token:
                depth += 1
                cursor += self._start_length
            elif string[cursor:cursor + self._stop_length] == self.stop_token:
                depth -= 1
                if depth == 0:
                    break
                cursor += self._stop_length
            elif string[cursor] in self.quotes:
                cursor = self._skip_string(cursor, string)
            else:
                cursor += 1
        else:
            raise ValueError(f'failed to parse {string!r}: unmatched {self.start_token!r} at offset {cursor}')
        return cursor

    def _skip_string(self, cursor, string):
        quote = string[cursor]
        cursor += 1
        while cursor < len(string):
            if string[cursor] == quote:
                cursor += 1
                break
            if string[cursor] == self.string_escape:
                cursor += 2
            else:
                cursor += 1
        else:
            raise ValueError(f'failed to parse {string!r}: unterminated string at offset {cursor}')
        return cursor

    def _evaluate(self, code, namespace):
        if '!' in code:
            code, conversion = code.split('!', 1)
            if conversion not in self.converters:
                raise SyntaxError(f"failed to evaluate {code!r}: invalid conversion character {conversion!r} (expected {concat(self.converters)})")
            converter = self.converters[conversion]
        else:
            converter = str
        try:
            result = eval(code, namespace)
        except SyntaxError as error:
            offset = error.offset - 1
            if error.text[offset] == ':':
                code, format = code[:offset], code[offset + 1:]
                result = eval(code, namespace)
                result = result.__format__(format)
            else:
                raise
        return converter(result)