
class SymbolTable:

    def __init__(self) -> None:
        self.keywords = ['if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return', 'endif']
        self.id = []

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
    