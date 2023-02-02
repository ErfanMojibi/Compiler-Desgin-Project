class SymbolTable:

    def __init__(self) -> None:
        self.keywords = ['if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return', 'endif']
        self.id = ['output']
        self.line_dict = dict()
        self.symbol_table_out = []
        self.table = dict()
        self.table['output'] = {"type": "0", "address": -2}

    def get_string_token_type(self, string):
        if string in self.keywords:
            return 'KEYWORD'
        else:
            return 'ID'

    def is_id(self, string):
        if string in self.id:
            return True
        else:
            return False

    def insert_id(self, string):
        if string not in self.keywords and string not in self.id:
            self.id.append(string)
            self.table[string] = {"type": "-1", "address": -1}

    def export_symbol_table(self):
        i = 1
        out_str = ''
        for string in self.keywords + self.id:
            out_str += str(i) + '.\t' + str(string) + '\n'
            i += 1

        f_out = open('symbol_table.txt', 'w')
        f_out.write(out_str)
        f_out.close()
