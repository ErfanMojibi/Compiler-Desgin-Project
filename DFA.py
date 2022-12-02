class Transition:
    def __init__(self, start, end, accepted_chars, error_message='', error=False):
        self.start = start
        self.end = end
        self.accepted_chars = accepted_chars
        self.error = error
        self.error_message = error_message

    def check_transition(self, char):
        return char in self.accepted_chars

    def is_valid_transition(self):
        return not self.error

    def get_error_message(self):
        return self.error_message

    def __str__(self):
        return f"{self.start} => {self.end}; chars:{self.accepted_chars}\n"


class DFA:
    def __init__(self, states, alphabet, transition_function, start_state, accept_states, token_types):
        self.states = states
        self.alphabet = alphabet
        self.transition_function = transition_function
        self.start_state = start_state
        self.accept_states = accept_states
        self.current_state = start_state
        self.error = False
        self.error_message = ''
        self.token_types = token_types

    def move(self, current_input):
        for transition in self.transition_function:
            if transition.start == self.current_state and transition.check_transition(current_input):
                self.current_state = transition.end
                self.error = transition.error
                self.error_message = transition.error_message
                break
        if current_input not in alphabets:
            self.error = True
            self.error_message = 'Invalid input'
            self.current_state = 'invalid_input'

    def is_finished(self):
        return self.current_state in self.accept_states

    def get_token_type(self):
        if self.is_finished and not self.error:
            return self.token_types[self.current_state]
        else:
            return

    def reset(self):
        self.current_state = self.start_state


digits = {'0', '1', '2', '3', '4', '5', '8', '7', '8', '9'}
letters = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
           'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
           'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'}
symbols = {';', ':', '(', ')', '[', ']', '{', '}', '+', '-', '*', '/', '<', '==', '=', ','}
white_space = {' ', '\n', '\t', '\r', '\f', '\v'}
extra_symbols = {'#'}

alphabets = digits.union(letters, symbols, white_space)

all = {chr(i) for i in range(256)}

dfa_states_reminder = {
    's': 0,
    'num': 1,
    'num_ac': 2,
    'white_space': 16,
    'id_key': 3,
    'division': 50,
    'id_key_ac': 4,

    'white_space_ac': 21,
    'symbol': 5,
    'equ_symbol': 6,
    'd_equ_symbol': 7,
    'equ_symbol_ac': 8,

    'star': 17,
    'star_ac': 12,
    'unclosed_comment': 18,
    'comment': 9,
    'line_comment': 11,
    'line_comment_2': 13,

    'invalid_input': 100000,

    'long_comment': 10,
    'long_comment_1': 14,
    'long_comment_2': 15,
    'EOF' : 1000,
    
    'unclosed_comment_2': 19,
}
transition_function = [
    Transition('s', 'num', digits),
    Transition('s', 'id_key', letters),

    Transition('s', 'white_space', white_space),
    Transition('white_space', 'white_space', white_space),
    Transition('white_space', 'white_space_ac', alphabets - white_space),

    Transition('id_key', 'id_key', letters.union(digits)),
    Transition('id_key', 'id_key_ac', alphabets - letters.union(digits)),

    Transition('num', 'num', digits),
    Transition('num', 'num_ac', symbols.union(white_space)),
    Transition('num', 'num_ac', alphabets - white_space.union(symbols), error=True, error_message='Invalid number'),

    Transition('s', 'equ_symbol', {'='}),
    Transition('equ_symbol', 'd_equ_symbol', {'='}),
    Transition('equ_symbol', 'equ_symbol_ac', alphabets - {'='}),

    Transition('s', 'star', {'*'}),
    Transition('star', 'unclosed_comment', {'\\'}, error=True, error_message='not proper comment'),
    Transition('star', 'star_ac', alphabets - {'\\'}),

    Transition('s', 'comment', {'/'}),
    Transition('comment', 'division', alphabets - {'*', '/'}),
    Transition('comment', 'line_comment', {'/'}),
    Transition('line_comment', 'line_comment', all - {'\n', 5}),
    Transition('line_comment', 'line_comment_2', {5, '\n'}),

    Transition('comment', 'long_comment', {'*'}),
    Transition('long_comment', 'long_comment_1', {'*'}),
    Transition('long_comment', 'unclosed_comment_2', {5}, error=True,
               error_message='unclosed comment reached end of the file'),

    Transition('long_comment_1', 'long_comment_2', {'/'}),
    Transition('long_comment_1', 'unclosed_comment_2', {5}, error=True,
               error_message='unclosed comment reached end of the file'),
    Transition('long_comment_1', 'long_comment', alphabets - {5, '*'}),

    Transition('s', 'symbol', symbols - {'=', '/'}),
    Transition('s', 'EOF', {5})
]

accept_states = ['unclosed_comment_2', 'long_comment_2', 'unclosed_comment', 'line_comment_2', 'star_ac', 'id_key_ac',
                 'd_equ_symbol', 'num_ac', 'white_space_ac', 'symbol', 'equ_symbol_ac', 'division', 'EOF', 'invalid_input']

token_types = {'long_comment_2': 'COMMENT',
               'line_comment_2': 'COMMENT',
               'star_ac': 'SYMBOL',
               'id_key_ac': 'ID_KEY',
               'num_ac': 'NUM',
               'white_space_ac': 'white_space',
               'symbol': 'SYMBOL',
               'equ_symbol_ac': 'SYMBOL',
               'd_equ_symbol' : 'SYMBOL',
               'division': 'SYMBOL',
               }
dfa = DFA(dfa_states_reminder.keys(), alphabets, transition_function, 's', accept_states, token_types)
