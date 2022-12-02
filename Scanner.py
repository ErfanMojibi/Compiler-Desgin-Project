from DFA import dfa
from SymbolTable import SymbolTable


class Scanner:

    def __init__(self, input_file, scanner_dfa):
        self.file = open(input_file)
        self.reach_end_of_file = False
        self.dfa = scanner_dfa
        self.look_ahead = None
        self.line_no = 1
        self.tokens = []
        self.symbol_table = SymbolTable()
        self.errors = []
        self.panic_chars = ['\n', ';']

    def get_look_ahead(self):
        return self.look_ahead

    def move_look_ahead(self):
        if not self.reach_end_of_file:
            self.look_ahead = self.file.read(1)
            if self.look_ahead == '\n':
                self.line_no += 1
            if self.look_ahead == '':
                self.reach_end_of_file = True
        else:
            self.look_ahead = ''

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
        
        line_number_start = self.line_no
        
        while not self.dfa.is_finished():
            self.dfa.move(self.look_ahead)
            
            if not self.dfa.is_finished():
                buffer += self.look_ahead
                self.move_look_ahead()

        if self.dfa.get_token_type() == 'id_key':
            if self.symbol_table.get_string_token_type(buffer) == 'ID':
                self.symbol_table.insert_id(buffer)
            return (line_number_start ,self.symbol_table.get_string_token_type(buffer), buffer)
        else:
            if self.dfa.error == True:
                self.errors.append((line_number_start, (buffer), self.dfa.error_message))
                # todo copy 
                buffer = ''
                self.move_look_ahead()
                return None
            else:
                if self.dfa.current_state in ['long_comment_2', 'line_comment_2', 'd_equ_symbol', 'symbol']:
                    buffer += self.look_ahead
                    self.move_look_ahead()
                return (line_number_start ,self.dfa.get_token_type(), buffer)

    def get_all_tokens_and_export(self):
        while not self.reach_end_of_file:
            self.tokens.append(self.get_next_token())
        
        self.export_tokens()
        self.symbol_table.export_symbol_table()
        self.export_errors()
    
    def export_errors(self):
        line_nu = 0
        out_str = ''
        if len(self.errors) > 0:
            line_nu = self.errors[0][0]
            for er in self.errors:
                if er[0] != line_nu:
                    out_str += '\n' + str(er[0]) + '.\t'
                line_nu = er[0]
                out_str += '(' + er[1] + ',' + er[2] + ') '
        else:
            out_str = 'There is no lexical error.\n'


    
    def export_tokens(self):
        line_number = -1

        out_str = ''
        for token in self.tokens:
            if token[1] != 'white_space' and token[1] != 'comment':
                if token[0] != line_number:
                    out_str += '\n' + str(token[0]) + '.\t'
                line_number = token[0]
                out_str += '(' + token[1] + ',' + token[2] + ') '
        token_file = open('tokens.txt', 'w')
        token_file.write(out_str)
        token_file.close()


scanner = Scanner("input.txt", dfa)
scanner.get_all_tokens_and_export()
