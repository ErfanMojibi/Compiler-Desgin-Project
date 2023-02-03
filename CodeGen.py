class CodeGenerator:
    def __init__(self, symbol_table, grammar):
        self.semantic_stack = []
        self.program_block = []
        self.temp_address = 500
        self.symbol_table = symbol_table
        self.grammar = grammar
        self.break_temp_address = []
        self.where_to_break = []

    def get_temp(self, var_size=4):
        self.temp_address += var_size
        return self.temp_address - var_size

    def find_address(self, name):
        if name in self.symbol_table.table:
            return self.symbol_table.table[name]['address']
        else:
            return -1

    def pop_from_semantic_stack(self, size):
        for i in range(size):
            self.semantic_stack.pop()

    def p_id_index(self, token):
        self.semantic_stack.append(token[2])

    def p_num(self, token):
        self.semantic_stack.append('#' + token[2])

    def p_type(self, token):
        self.semantic_stack.append(token[2])

    def p_id(self, token):
        address = self.find_address(token[2])
        self.semantic_stack.append(address)

    def p_op(self, token):
        self.semantic_stack.append(token[2])

    def p_num_temp(self, token):
        self.semantic_stack.append('#' + token[2])

    def declare_func(self, token):
        # TODO
        pass

    def save(self, size=1):
        for _ in range(size):
            self.program_block.append(None)
            self.semantic_stack.append(len(self.program_block) - 1)

    def jpf(self):
        self.program_block[self.semantic_stack[-1]] = f'(JPF, {self.semantic_stack[-2]}, {len(self.program_block)}, )'
        self.pop_from_semantic_stack(2)

    def jpf_save(self):
        self.program_block[
            self.semantic_stack[-1]] = f'(JPF, {self.semantic_stack[-2]}, {len(self.program_block) + 1}, )'

        self.pop_from_semantic_stack(2)

        self.save()

    def jp(self):
        self.program_block[self.semantic_stack[-1]] = f'(JP, {len(self.program_block)}, , )'
        self.pop_from_semantic_stack(1)

    def assign(self):
        res = self.semantic_stack[-2]
        self.program_block.append(f'(ASSIGN, {self.semantic_stack[-1]}, {self.semantic_stack[-2]}, )')
        self.pop_from_semantic_stack(2)
        self.semantic_stack.append(res)

    def declare(self):
        lexeme = self.semantic_stack[-1]
        var_type = self.semantic_stack[-2]
        var_size = 4 if var_type == 'int' else 1
        address = self.get_temp(var_size)
        self.symbol_table.table[lexeme]["address"] = address
        self.program_block.append(f'(ASSIGN, #0, {address}, )')
        self.pop_from_semantic_stack(2)

    def add(self):
        address1, address2 = self.semantic_stack[-1], self.semantic_stack[-3]
        op = self.semantic_stack[-2]
        temp = self.get_temp()
        operation = 'ADD' if op == '+' else 'SUB'
        self.program_block.append(f'({operation}, {address2}, {address1}, {temp})')

        self.pop_from_semantic_stack(3)
        self.semantic_stack.append(temp)

    def mult(self):
        address1, address2 = self.semantic_stack[-1], self.semantic_stack[-3]
        op = self.semantic_stack[-2]
        temp = self.get_temp()
        operation = 'MULT' if op == '*' else 'DIV'
        self.program_block.append(f'({operation}, {address2}, {address1}, {temp})')

        self.pop_from_semantic_stack(3)
        self.semantic_stack.append(temp)

    def rel(self):
        address1, address2 = self.semantic_stack[-1], self.semantic_stack[-3]
        op = self.semantic_stack[-2]
        temp = self.get_temp()
        operation = 'EQ' if op == '==' else 'LT'
        self.program_block.append(f'({operation}, {address2}, {address1}, {temp})')

        self.pop_from_semantic_stack(3)
        self.semantic_stack.append(temp)

    def pop_exp(self):
        self.pop_from_semantic_stack(1)

    def call(self):
        address = self.semantic_stack[-2]
        if address == -2:
            self.program_block.append(f'(PRINT, {self.semantic_stack[-1]}, , )')
            self.pop_from_semantic_stack(1)

    def while_start(self):
        break_temp = self.get_temp()
        self.break_temp_address.append(break_temp)
        # save one empty place for break
        self.program_block.append(f'(ASSIGN, #0, {break_temp}, )')
        self.where_to_break.append(len(self.program_block))
        self.program_block.append(None)

        self.semantic_stack.append(len(self.program_block))

    def while_end(self):
        pc = len(self.program_block)
        self.program_block[self.semantic_stack[-1]] = f'(JPF, {self.semantic_stack[-2]}, {pc + 1}, )'
        self.program_block.append(f'(JP, {self.semantic_stack[-3]}, , )')
        self.program_block[self.where_to_break[-1]] = f'(ASSIGN, #{pc + 1}, {self.break_temp_address[-1]}, )'
        self.pop_from_semantic_stack(3)

        self.where_to_break.pop()
        self.break_temp_address.pop()

    def switch_start(self):
        break_temp = self.get_temp()
        self.break_temp_address.append(break_temp)
        # save one empty place for break
        self.program_block.append(f'(ASSIGN, #0, {break_temp}, )')
        self.where_to_break.append(len(self.program_block))
        self.program_block.append(None)

    def switch_end(self):
        self.semantic_stack.pop()  # pop expression
        self.program_block[
            self.where_to_break[-1]] = f'(ASSIGN, #{len(self.program_block)}, {self.break_temp_address[-1]}, )'
        self.where_to_break.pop()
        self.break_temp_address.pop()

    def break_jp(self):
        self.program_block.append(f'(JP, @{self.break_temp_address[-1]}, , )')

    def while_condition(self):
        self.save()

    def declare_array(self):
        lexeme = self.semantic_stack[-2]
        var_type = self.semantic_stack[-3]
        var_size = 4 if var_type == 'int' else 1
        arr_len = self.semantic_stack[-1]
        address = self.get_temp(int(arr_len[1:]) * var_size)
        self.symbol_table.table[lexeme]["address"] = address
        self.program_block.append(f'(ASSIGN, #0, {address}, )')
        self.pop_from_semantic_stack(3)

    def array_access(self):
        address = self.semantic_stack[-2]
        index = self.semantic_stack[-1]
        if str(index).startswith('#'):
            index_address = address + 4 * int(index[1:])
            self.pop_from_semantic_stack(2)
            self.semantic_stack.append(index_address)
        else:
            temp = self.get_temp()
            self.program_block.append(f'(MULT, {index}, #4, {temp})')
            self.program_block.append(f'(ADD, #{address}, {temp}, {temp})')
            self.pop_from_semantic_stack(2)
            self.semantic_stack.append(f'@{temp}')

    def fake_save(self):
        self.semantic_stack.append(f'#{0}')
        self.save()

    def case_condition(self, num):
        temp = self.get_temp()
        self.program_block.append(f'(EQ, #{num}, {self.semantic_stack[-1]}, {temp})')
        self.semantic_stack.append(temp)

    def generate_code(self, token, rule_no):
        rule = self.grammar[rule_no]
        rule_rhs = rule[2:]
        rule_no = int(rule_no)
        if rule_no == 67:  # p_id_index
            self.p_id_index(token)
        elif rule_no == 68:  # p_num
            self.p_num(token)
        elif rule_no == 69:  # p_type
            self.p_type(token)
        elif rule_no == 70:  # p_id
            self.p_id(token)
        elif rule_no == 71:  # p_op
            self.p_op(token)
        elif rule_no == 72:  # p_num_temp
            self.p_num_temp(token)
        elif rule_no == 73:  # declare_func
            pass
        elif rule_no == 74:  # save
            self.save()
        elif rule_no == 75:  # jpf_save
            self.jpf_save()
        elif rule_no == 76:  # while_start
            self.while_start()
        elif rule_no == 77:  # while_condition
            self.while_condition()
        elif rule_no == 78:  # switch_start
            self.switch_start()
        elif rule_no == 6 or rule_no == 15 or rule_no == 16:  # declare for var_declaration and param
            self.declare()
        elif rule_no == 7:  # declare_array
            self.declare_array()
        elif rule_no == 28:  # pop_exp
            self.pop_exp()
        elif rule_no == 29:  # break_jp
            self.break_jp()
        elif rule_no == 31 or rule_no == 80:  # jpf
            self.jpf()
        elif rule_no == 32:  # jp
            self.jp()
        elif rule_no == 33:  # while_end
            self.while_end()
        elif rule_no == 42:  # assign
            self.assign()
        elif rule_no == 45:  # array_access
            self.array_access()
        elif rule_no == 46:  # rel
            self.rel()
        elif rule_no == 50:  # add
            self.add()
        elif rule_no == 54:  # mult
            self.mult()
        elif rule_no == 62:  # call
            self.call()
        elif rule_no == 79:  # fake_save : always true
            self.fake_save()
        elif rule_no == 36:  # switch_end
            self.switch_end()
        elif rule_no == 81:  # case_condition
            self.case_condition(token[2])

    def export_PB(self):
        with open('output.txt', 'w') as f:
            for index, line in enumerate(self.program_block):
                f.write(f'   {line}\n')
