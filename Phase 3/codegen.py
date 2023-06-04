class CodeGenerator:
    def __init__(self):
        self.current_type = None
        self.current_lexeme = None
        self.current_size = None
        self.prev_state = 0
        # save 500 for return address and 504 for return value
        self.current_variable = 512
        self.symbol_table = list()
        self.code_block = list()
        self.semantic_stack = list()
        self.variable_addresses = set()
        self.break_stack = list()
        self.first_case = False
        self.iter_counter = -1
        self.alternative = {'+': 'ADD', '-': 'SUB', '*': 'MULT', '/': 'DIV', '<': 'LT', '==': 'EQ'}
        self.current_function = None
        self.function_params = dict()
        self.function_args = list()
        self.code_block.append('(ASSIGN, #0, 500,   )')
        self.code_block.append('(ASSIGN, #0, 504,   )')
        self.scope_stack = list()
        self.code_block.append(None)
        self.code_block.append(None)
        self.code_block.append(None)
        self.function_params['output'] = [('output_var', 'int', 508)]
        self.symbol_table.append(('output', 'function', len(self.code_block)))
        self.code_block.append('(PRINT, 508,  ,   )')
        self.code_block.append('(JP, @500,  ,   )')

    def get_temp(self):
        self.current_variable += 4
        return self.current_variable - 4

    def find_var(self, var_name):
        for entry in self.symbol_table:
            if entry[0] == var_name:
                return entry[2]
        return False

    def find_lexeme(self, address):
        for entry in self.symbol_table:
            if entry[2] == address:
                return entry[0]
        return False

    def get_array(self, array_size):
        self.current_variable += 4 * array_size
        return self.current_variable - 4 * array_size

    def complete_breaks(self):
        while len(self.break_stack) > 0 and self.break_stack[-1][1] == self.iter_counter:
            self.code_block[self.break_stack[-1][0]] = f'(JP, {len(self.code_block)},  ,   )'
            self.break_stack.pop()
        self.iter_counter -= 1

    def get_type(self, address):
        for entry in self.symbol_table:
            if entry[2] == address:
                return entry[1]
        return False

    def generate(self, action, input=None):
        # print(self.symbol_table)
        # print(self.code_block)
        # print(self.semantic_stack)
        # print(self.scope_stack)
        # print(action)
        if action == 'def_type':
            self.current_type = input
        elif action == 'pid':
            found = self.find_var(input)
            if found:
                self.semantic_stack.append(found)
            elif self.current_type:
                self.current_lexeme = input
            else:
                self.semantic_stack.append(self.get_temp())
        elif action == 'parray':
            temp = self.get_temp()
            self.code_block.append(f'(MULT, #4, {self.semantic_stack[-1]}, {temp} )')
            self.code_block.append(f'(ADD, {temp}, #{self.semantic_stack[-2]}, {temp} )')
            self.variable_addresses.add(temp)
            self.semantic_stack.pop()
            self.semantic_stack.pop()
            self.semantic_stack.append(temp)
        elif action == 'def_singular':
            self.symbol_table.append((self.current_lexeme, self.current_type, self.get_temp()))
            self.current_lexeme = None
            self.current_type = None
        elif action == 'def_array_size':
            self.current_size = input
        elif action == 'save_state':
            self.prev_state = len(self.semantic_stack)
        elif action == 'remove_cache':
            self.semantic_stack = self.semantic_stack[0:self.prev_state]
        elif action == 'def_array':
            self.symbol_table.append((self.current_lexeme, 'array', self.get_array(int(self.current_size) if self.current_size else 1)))
            self.current_lexeme = None
            self.current_type = None
            self.current_size = None
        elif action == 'save_if':
            self.semantic_stack.append(len(self.code_block))
            self.code_block.append(None)
        elif action == 'save_while':
            self.semantic_stack.append(len(self.code_block))
            self.scope_stack.append(len(self.symbol_table))
            self.code_block.append(None)
        elif action == 'jpf_save':
            self.code_block.append(None)
            self.code_block[self.semantic_stack[-1]] = f'(JPF, {self.semantic_stack[-2]}, {len(self.code_block)},   )'
            self.semantic_stack.pop()
            self.semantic_stack.pop()
            self.semantic_stack.append(len(self.code_block) - 1)
        elif action == 'jp':
            self.code_block[self.semantic_stack[-1]] = f'(JP, {len(self.code_block)},  ,   )'
            self.semantic_stack.pop()
        elif action == 'jpf':
            self.code_block[self.semantic_stack[-1]] = f'(JPF, {self.semantic_stack[-2]}, {len(self.code_block)},   )'
            self.semantic_stack.pop()
            self.semantic_stack.pop()
        elif action == 'label':
            self.semantic_stack.append(len(self.code_block))
            self.iter_counter += 1
        elif action == 'whil':
            self.semantic_stack = self.semantic_stack[0:self.scope_stack[-1]]
            self.scope_stack.pop()
            self.code_block[
                self.semantic_stack[-1]] = f'(JPF,{self.semantic_stack[-2]}, {len(self.code_block) + 1},   )'
            self.code_block.append(f'(JP, {self.semantic_stack[-3]},  ,   )')
            self.semantic_stack.pop()
            self.semantic_stack.pop()
            self.semantic_stack.pop()
            self.complete_breaks()
        elif action == 'save_op':
            self.semantic_stack.append(input)
        elif action == 'assign':
            # print(self.code_block)
            # print(self.semantic_stack)
            self.code_block.append(
                f'(ASSIGN, {"@" if self.semantic_stack[-1] in self.variable_addresses else ""}{self.semantic_stack[-1]}, {"@" if self.semantic_stack[-2] in self.variable_addresses else ""}{self.semantic_stack[-2]},   )')
            self.semantic_stack.pop()
        elif action in ['apply_rel', 'apply_mul', 'apply_add']:
            temp = self.get_temp()
            self.code_block.append(
                f'({self.alternative[self.semantic_stack[-2]]}, {"@" if self.semantic_stack[-3] in self.variable_addresses else ""}{self.semantic_stack[-3]}, '
                f'{"@" if self.semantic_stack[-1] in self.variable_addresses else ""}{self.semantic_stack[-1]}, {temp} )')
            self.symbol_table.append((None, self.get_type(self.semantic_stack[-1]), temp))
            self.semantic_stack.pop()
            self.semantic_stack.pop()
            self.semantic_stack.pop()
            self.semantic_stack.append(temp)
        elif action == 'constant':
            temp = self.get_temp()
            self.symbol_table.append((None, 'int', temp))
            self.code_block.append(f'(ASSIGN, #{input}, {temp},   )')
            self.semantic_stack.append(temp)
        elif action == 'print':
            self.code_block.append(
                f'(PRINT, {"@" if self.semantic_stack[-1] in self.variable_addresses else ""}{self.semantic_stack[-1]},  ,   )')
            self.semantic_stack.pop()
        elif action == 'get_out':
            self.break_stack.append((len(self.code_block), self.iter_counter))
            self.code_block.append(None)
        elif action == 'start_switch':
            self.scope_stack.append(len(self.symbol_table))
            self.iter_counter += 1
            self.first_case = True
        elif action == 'new_case':
            if not self.first_case:
                self.code_block[
                    self.semantic_stack[-1]] = f'(JPF, {self.semantic_stack[-2]}, {len(self.code_block)},   )'
                self.semantic_stack.pop()
                self.semantic_stack.pop()
            self.first_case = False
        elif action == 'complete_case':
            temp = self.get_temp()
            self.code_block.append(f'(EQ, {self.semantic_stack[-1]}, {self.semantic_stack[-2]}, {temp} )')
            self.semantic_stack.pop()
            self.semantic_stack.append(temp)
            self.semantic_stack.append(len(self.code_block))
            self.code_block.append(None)
        elif action == 'switch_default':
            if not self.first_case:
                self.code_block[
                    self.semantic_stack[-1]] = f'(JPF, {self.semantic_stack[-2]}, {len(self.code_block)},   )'
                self.semantic_stack.pop()
                self.semantic_stack.pop()
            self.semantic_stack.pop()
            self.first_case = False
        elif action == 'end_switch':
            self.symbol_table = self.symbol_table[0:self.scope_stack[-1]]
            self.scope_stack.pop()
            self.complete_breaks()
            self.first_case = False
        elif action == 'init_param':
            self.function_params[self.current_function] = [self.symbol_table[-1]]
        elif action == 'add_param':
            self.function_params[self.current_function].append(self.symbol_table[-1])
        elif action == 'add_function':
            self.function_params[self.current_function] = list()
        elif action == 'push_arg':
            self.function_args.append(self.semantic_stack[-1])
            self.semantic_stack.pop()
        elif action == 'function_proto':
            self.symbol_table.append((self.current_lexeme, 'function', len(self.code_block)))
            self.current_function = self.current_lexeme
            self.scope_stack.append(len(self.symbol_table))
            self.current_type = None
            self.current_lexeme = None
        elif action == 'jr':
            self.symbol_table = self.symbol_table[0:self.scope_stack[-1]]
            self.scope_stack.pop()
            self.code_block.append(f'(JP, @500,  ,   )')
        elif action == 'jal':
            temp_address = self.get_temp()
            temp_return = self.get_temp()
            change_return = self.get_temp()
            try:
                for i in range(len(self.function_args)):
                    self.code_block.append(
                        f'(ASSIGN, {"@" if self.function_args[i] in self.variable_addresses else ""}{self.function_args[i]}, {self.function_params[self.find_lexeme(self.semantic_stack[-1])][i][2]},   )')
            except:
                pass
            self.code_block.append(f'(ASSIGN, 500, {temp_address},   )')
            self.code_block.append(f'(ASSIGN, 504, {temp_return},   )')
            self.code_block.append(f'(ASSIGN, #{len(self.code_block) + 2}, 500,   )')
            self.code_block.append(f'(JP, {self.semantic_stack[-1]},  ,   )')
            self.code_block.append(f'(ASSIGN, 504, {change_return},   )')
            self.code_block.append(f'(ASSIGN, {temp_address}, 500,   )')
            self.code_block.append(f'(ASSIGN, {temp_return}, 504,   )')
            self.semantic_stack.pop()
            self.semantic_stack.append(change_return)
            self.function_args.clear()
        elif action == 'back':
            self.code_block.append(f'(JP, @500,  ,   )')
        elif action == 'return_value':
            self.code_block.append(f'(ASSIGN, {self.semantic_stack[-1]}, 504,   )')
            self.semantic_stack.pop()

    def semantic_analysis(self, action, input=None):
        if action == 'pid':
            found = self.find_var(input)
            if not found and not self.current_type:
                return f'\'{input}\' is not defined.'
            return None
        elif action == 'jal':
            if len(self.function_args) != len(self.function_params[self.find_lexeme(self.semantic_stack[-1])]):
                return f'Mismatch in numbers of arguments of \'{self.find_lexeme(self.semantic_stack[-1])}\'.'
            for i in range(len(self.function_args)):
                if self.get_type(self.function_args[i]) and self.get_type(self.function_args[i]) != self.function_params[self.find_lexeme(self.semantic_stack[-1])][i][1]:
                    return f'Mismatch in type of argument {i + 1} of \'{self.find_lexeme(self.semantic_stack[-1])}\'. Expected \'{self.function_params[self.find_lexeme(self.semantic_stack[-1])][i][1]}\' but got \'{self.get_type(self.function_args[i])}\' instead.'
            return None
        elif action == 'def_singular':
            if self.current_type == 'void':
                return f'Illegal type of void for \'{self.current_lexeme}\'.'
        elif action in ['apply_rel', 'apply_mul', 'apply_add']:
            if self.get_type(self.semantic_stack[-1]) and self.get_type(self.semantic_stack[-3]) and self.get_type(self.semantic_stack[-1]) != self.get_type(self.semantic_stack[-3]):
                return f'Type mismatch in operands, Got {self.get_type(self.semantic_stack[-1])} instead of {self.get_type(self.semantic_stack[-3])}.'
            return None
        elif action == 'get_out':
            if self.iter_counter == -1:
                return 'No \'while\' or \'switch case\' found for \'break\'.'

    def set_start(self):
        self.code_block[2] = f'(ASSIGN, #4, 500,   )'
        self.code_block[3] = f'(JP, {self.find_var("main")},  ,   )'
        self.code_block[4] = f'(JP, {len(self.code_block)},  ,   )'
