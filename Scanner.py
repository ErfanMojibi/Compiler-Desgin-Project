from DFA import dfa
from SymbolTable import SymbolTable


class Scanner:

    def __init__(self, input_file, scanner_dfa):
        self.file = open(input_file)
        self.reach_end_of_file = False
        self.dfa = scanner_dfa
        self.look_ahead = None
        self.line_no = 1
        self.symbol_table = SymbolTable()
        self.errors = []
        self.panic_chars = ['\n', ';']

    def get_look_ahead(self):
        return self.look_ahead

    def move_look_ahead(self):
        if not self.reach_end_of_file:
            self.look_ahead = self.file.read(1)
            if self.look_ahead == None:
                self.reach_end_of_file = True
        else:
            self.look_ahead = ''
            if self.look_ahead == '\n':
                self.line_no += 1

    def get_line_number(self):
        return self.line_no

    def get_symbol_table(self):
        return self.symbol_table

    def get_errors(self):
        return self.errors
    
    def get_next_token(self):
        self.dfa.reset()
        buffer = ''
        
        if self.look_ahead == None and self.reach_end_of_file == False:
            self.move_look_ahead()
        
        while not self.dfa.is_finished():
            self.dfa.move(self.look_ahead)
            
            if not self.dfa.is_finished():
                buffer += self.look_ahead
                self.move_look_ahead()

        if self.dfa.get_token_type() == 'id_key':
            if self.symbol_table.get_string_token_type(buffer) == 'ID':
                self.symbol_table.insert_id(buffer)
            return (self.symbol_table.get_string_token_type(buffer), buffer)
        else:
            if self.dfa.error == True:
                self.errors.append((self.line_no, self.dfa.error_message))
                buffer = ''
                self.move_look_ahead()
                return None
            else:
                if self.dfa.current_state in ['long_comment_2', 'line_comment_2', 'd_equ_symbol', 'symbol']:
                    buffer += self.look_ahead
                    self.move_look_ahead()
                return (self.dfa.get_token_type(), buffer)


scanner = Scanner("input.txt", dfa)
