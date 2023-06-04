import json
from scanner import *
from Tree import *


class Parser:
    def __init__(self, filename):
        self.tree = Tree()
        json_content = json.load(open('table.json'))
        self.terminals = json_content['terminals']
        self.non_terminals = json_content['non_terminals']
        self.first = json_content['first']
        self.follow = json_content['follow']
        self.grammar = json_content['grammar']
        self.parse_table = json_content['parse_table']
        self.scanner = FullScanner(filename)
        self.syntax_errors = []
        self.current_line = None
        self.current_token = None
        self.token = None
        self.stack = ['0']
        self.id_stack = list()

    def has_goto(self, number):
        for key in self.parse_table[number]:
            if key in self.non_terminals:
                return True
        return False

    def is_in_follow(self, prev_state, non_terminal_set, terminal):
        for non_terminal in non_terminal_set:
            if terminal in self.follow[non_terminal]:
                return non_terminal
        return False

    def panic(self):
        while self.current_token not in self.parse_table[self.stack[-1]]:
            self.syntax_errors.append(f'#{self.current_line + 1} : syntax error , illegal {self.token[1]}')
            self.current_line, self.token = self.scanner.next_token()
            self.current_token = self.token[0] if self.token[0] not in ['KEYWORD', 'SYMBOL'] else self.token[1]
            while not self.has_goto(self.stack[-1]):
                if isinstance(self.stack[-2], str):
                    self.syntax_errors.append(f'syntax error , discarded {self.stack[-2]} from stack')
                else:
                    self.syntax_errors.append(
                        f'syntax error , discarded ({self.stack[-2][0]}, {self.stack[-2][1]}) from stack')
                self.id_stack.pop()
                self.stack.pop()
                self.stack.pop()
            goto = sorted([x for x in self.parse_table[self.stack[-1]] if x in self.non_terminals])
            while not self.is_in_follow(self.stack[-1], goto, self.current_token):
                if self.current_token == '$':
                    self.syntax_errors.append(f'#{self.current_line + 1} : syntax error , Unexpected EOF')
                    return False
                self.syntax_errors.append(
                    f'#{self.current_line + 1} : syntax error , discarded {self.token[1]} from input')
                self.current_line, self.token = self.scanner.next_token()
                self.current_token = self.token[0] if self.token[0] not in ['KEYWORD', 'SYMBOL'] else self.token[1]
            non_terminal = self.is_in_follow(self.stack[-1], goto, self.current_token)
            next_state = self.parse_table[self.stack[-1]][non_terminal].split('_')[1]
            self.syntax_errors.append(f'#{self.current_line + 1} : syntax error , missing {non_terminal}')
            self.stack.append(non_terminal)
            self.stack.append(next_state)
            self.id_stack.append(self.tree.add_new_node(non_terminal))
        return True


    def parse(self):
        while not self.scanner.is_end():
            self.current_line, self.token = self.scanner.next_token()
            self.current_token = self.token[0] if self.token[0] not in ['KEYWORD', 'SYMBOL'] else self.token[1]
            if not self.panic():
                return
            action, number = self.parse_table[self.stack[-1]][self.current_token].split('_')
            while not action == 'shift':
                current_grammar = self.grammar[number]
                to_remove = 0 if current_grammar[2] == 'epsilon' else len(current_grammar) - 2
                self.stack = self.stack[0:len(self.stack) - 2 * to_remove]
                current_id = self.tree.add_new_node(current_grammar[0])
                for i in range(to_remove):
                    self.tree.add_children(current_id, self.id_stack[-(to_remove - i)])
                if to_remove == 0:
                    self.tree.add_children(current_id, self.tree.add_new_node('epsilon'))
                self.id_stack = self.id_stack[0:len(self.id_stack) - to_remove]
                goto = self.parse_table[self.stack[-1]][current_grammar[0]].split('_')[-1]
                self.stack.append(current_grammar[0])
                self.id_stack.append(current_id)
                self.stack.append(goto)
                self.panic()
                action, number = self.parse_table[self.stack[-1]][self.current_token].split('_')
            self.stack.append(self.token)
            self.id_stack.append(self.tree.add_new_node(f'({self.token[0]}, {self.token[1]})'))
            self.stack.append(number)
        self.tree.add_children(len(self.tree.nodes) - 2, self.tree.add_new_node('$'))
        return self.tree
