import json as js


def read_json(file_name):
    with open(file_name) as f:
        read_dict = js.load(f)
        return [item[1] for item in read_dict.items()]


class Parser:
    def __init__(self, terminals, non_terminals, first, follow, grammar, parse_table, scanner):
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.first = first
        self.follow = follow
        self.grammer = grammar
        self.parse_table = parse_table
        self.scanner = scanner
        self.stack = ["0"]
        
    def process_action_string(self, action_string):
        if(action_string.startswith("shift")):
            return ("shift", action_string[6:  ]))
        elif(action_string.startswith("reduce")):
            return ("reduce", action_string[7:  ]))
    
    def shift(self, token, state):
        self.stack.append(token)
        self.stack.append(state)        
                
    def reduce(self, token, rule):
        rule = self.grammar[rule]
        to_reduce_nt = rule[0]
        rule_rhs = rule[1]
        for i in range(len(rule_rhs)):
            self.stack.pop()
            self.stack.pop()
        self.stack.append(rule[0])
        self.stack.append(self.parse_table[self.stack[-2]].get(to_reduce_nt))
        
    def parse(self):
        _, token, lexeme = self.scanner.get_next_token()
        if(self.parse_table[self.stack[-1]].get(token) != None):
            action = self.process_action_string(self.parse_table[self.stack[-1]].get(token))
            if(action[0] == "shift"):
                self.shift(token, action[1])
            elif(action[0] == "reduce"):
                self.reduce()
            elif(action[0] == "acc"):
                print("ACCEPTED")
        else: #error
            pass

terminals, non_terminals, first, follow, grammar, parse_table = read_json("table.json")
print(terminals, non_terminals, first, follow, grammar, parse_table, sep="\n")
