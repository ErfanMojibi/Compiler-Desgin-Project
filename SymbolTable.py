
class SymbolTable:

    def __init__(self) -> None:
        self.keywords = ['if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return', 'endif']
        self.id = []
        self.line_dict = dict()


    def get_string_token_type(self, string):
        if string in self.keywords:
            return 'keyword'
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
    
    def export_symbol_table(self):
        i = 1
        out_str = ''
        for string in self.id:
            out_str += str(i) + '.\t' + string + '\n'
            i += 1
        f_out = open('symbol_table.txt' ,'w')
        f_out.write(out_str)
        f_out.close()
