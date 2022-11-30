
class Transition:
    def __init__(self, start, end, accepted_chars):
        self.start = start
        self.end = end
        self.accepted_chars = accepted_chars
    def check_transition(self, char):
        return char in self.accepted_chars
        
class DFA:
    def __init__(self, states, alphabet, transition_function, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        self.transition_function = transition_function
        self.start_state = start_state
        self.accept_states = accept_states
        self.current_state = start_state
    
    def move(self, current_input):
        for transition in self.transition_function:
            if transition.start == self.current_state and transition.check_transition(current_input):
                self.current_state = transition.end
    
    def is_finished(self):
        return self.current_state in self.accept_states
    
    def reset(self):
        self.current_state = self.start_state
     

digits = set(['0','1','2','3','4','5','8','7','8','9'])
letters = set(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'])
symbols = set([';',':','(',')','[',']','{','}','+','-','*','/','<','==','='])
white_space = set([' ', '\n', '\t','\r', '\f', '\v'])

keywords = ['if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return', 'endif']
alphabets = digits.union(letters, symbols, white_space)

transition_function = [Transition(0, 1, digits), Transition(0, 3, letters),
                       Transition(1, 1, digits), Transition(1, 2, alphabets - letters.union(digits)),]

dfa = DFA([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17], alphabets, transition_function, 0, [2, 4, 7, 8, 12, 15, 13, 17])

dfa.move("a")
print(dfa.current_state)