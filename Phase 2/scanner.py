from node import Node


class Scanner:

    def __init__(self, txt: str):
        self.txt = txt
        self.txt = self.txt + chr(0)
        self.current_pointer = 0
        self.nodes = [Node() for _ in range(17)]
        self.valid_symbols = ";:,[](){}+-*=</"
        self.construct_dfa()
        self.identikey = []
        self.symbol_table_keywords = {'else', 'if', 'void', 'int', 'while', 'break', 'switch', 'default', 'case',
                                      'return', 'endif'}

    def is_valid_symbol(self, char):
        return char in self.valid_symbols

    def is_invalid_character(self, char):
        return not (char.isspace() or char.isalnum() or self.is_valid_symbol(char) or self.is_eof(char))

    def get_char(self):
        self.current_pointer += 1
        if self.current_pointer > len(self.txt):
            return None
        else:
            return self.txt[self.current_pointer - 1]

    def is_end(self):
        return self.current_pointer + 1 == len(self.txt)

    def back(self):
        self.current_pointer -= 1

    def is_eof(self, char):
        return ord(char) == 0

    def construct_dfa(self):
        self.nodes[0] = Node(nxt=lambda x: 1 if x.isdigit() else (3 if x.isalpha() else (
            6 if (self.is_valid_symbol(x) and x not in '/=*') else (
                5 if x == '=' else (7 if x == '/' else (14 if x.isspace() else (16 if x == '*' else None)))))))
        self.nodes[1] = Node(
            nxt=lambda x: 1 if x.isdigit() else (
                2 if (x.isspace() or self.is_valid_symbol(x) or self.is_eof(x)) else None),
            error=lambda x: 'Invalid number' if x.isalpha() else None)
        self.nodes[2] = Node(star=True, terminal='NUM')
        self.nodes[3] = Node(
            nxt=lambda x: 3 if x.isalnum() else (
                4 if (self.is_valid_symbol(x) or x.isspace() or self.is_eof(x)) else None))
        self.nodes[4] = Node(star=True, terminal='ID')
        self.nodes[5] = Node(
            nxt=lambda x: 6 if x == '=' else (
                8 if (x.isspace() or self.is_valid_symbol(x) or x.isalnum() or self.is_eof(x)) else None))
        self.nodes[6] = Node(terminal='SYMBOL')
        self.nodes[7] = Node(nxt=lambda x: 12 if x == '/' else (
            9 if x == '*' else (
                8 if (x.isspace() or self.is_valid_symbol(x) or x.isalnum or self.is_eof(x)) else None)))
        self.nodes[8] = Node(star=True, terminal='SYMBOL')
        self.nodes[9] = Node(nxt=lambda x: 10 if x == '*' else 9,
                             error=lambda x: 'Unclosed comment' if (x == '\n' or self.is_eof(x)) else None)
        self.nodes[10] = Node(nxt=lambda x: 10 if x == '*' else (11 if x == '/' else 9),
                              error=lambda x: 'Unclosed comment' if (x == '\n' or self.is_eof(x)) else None)
        self.nodes[11] = Node(terminal='COMMENT')
        self.nodes[12] = Node(nxt=lambda x: 13 if x == '\n' else 12)
        self.nodes[13] = Node(star=True, terminal='COMMENT')
        self.nodes[14] = Node(
            nxt=lambda x: 14 if x.isspace() else (
                15 if (self.is_valid_symbol(x) or x.isalnum() or self.is_eof(x) or self.is_invalid_character(
                    x)) else None))
        self.nodes[15] = Node(star=True, terminal='WHITESPACE')
        self.nodes[16] = Node(nxt=lambda x: 8 if (
                (self.is_valid_symbol(x) and x != '/') or x.isspace() or self.is_eof(x) or x.isalnum()) else None,
                              error=lambda x: 'Unmatched comment' if x == '/' else None)

    def next_token(self):
        current_node = 0
        current_str = ''
        while not self.nodes[current_node].terminal:
            tmp = self.get_char()
            current_str += tmp
            if self.nodes[current_node].error and self.nodes[current_node].error(tmp):
                return 'ERROR', (self.nodes[current_node].error(tmp), current_str)
            elif self.nodes[current_node].get_next(current_str[-1]):
                current_node = self.nodes[current_node].get_next(current_str[-1])
            elif self.is_invalid_character(tmp):
                return 'ERROR', ('Invalid input', current_str)
        # print(current_node, len(self.txt), self.current_pointer)
        if self.nodes[current_node].star:
            current_str = current_str[:-1]
            self.back()
        token_type = self.nodes[current_node].terminal
        if token_type == 'ID' and current_str in self.symbol_table_keywords:
            token_type = 'KEYWORD'
        if (token_type == 'ID' or token_type == 'KEYWORD') and current_str not in self.identikey:
            self.identikey.append(current_str)
        return token_type, current_str


class FullScanner:
    def __init__(self, filename):
        lines = open(filename).readlines()
        lines[-1] = lines[-1].strip() + '\n'
        self.lines = lines
        self.current_line_scanner = None
        self.current_line = -1

    def next_token(self):
        while (self.current_line == -1 or self.current_line_scanner.is_end()) and self.current_line + 1 < len(self.lines):
            self.current_line += 1
            self.current_line_scanner = Scanner(self.lines[self.current_line])
        if self.current_line_scanner.is_end():
            self.current_line += 1
            return self.current_line, ('SYMBOL', '$')
        tmp = self.current_line_scanner.next_token()
        if tmp[0] == 'ERROR' and tmp[1][0] == 'Unclosed comment' and self.current_line + 1 < len(self.lines):
            self.lines[self.current_line + 1] = tmp[1][1].strip() + self.lines[self.current_line + 1]
            return self.next_token()
        elif tmp[0] == 'WHITESPACE' or tmp[0] == 'COMMENT' or tmp[0] == 'ERROR':
            return self.next_token()
        return self.current_line, tmp

    def is_end(self):
        return self.current_line == len(self.lines)
