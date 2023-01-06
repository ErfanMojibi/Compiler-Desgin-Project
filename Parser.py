import json as js
import anytree as at

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
        self.grammar = grammar
        self.parse_table = parse_table
        self.scanner = scanner
        self.stack = ["0"]
        self.tree_stack = []
    
        
    def process_action_string(self, action_string):
        if(action_string.startswith("shift")):
            return ("shift", action_string[6:  ])
        elif(action_string.startswith("reduce")):
            return ("reduce", action_string[7:  ])
        elif action_string.startswith("accept"):
            return ("accept",)
    
        
    def where_to_goto(self, goto_string):
        return goto_string[5:]
    
    
    def shift(self, token_terminal, state):
        self.stack.append(token_terminal)
        self.stack.append(state)
        # print("stack after shift:", self.stack)
        self.tree_stack.append(at.Node(f"({self.token[1]}, {self.token[2]})"))       
        self.to_get_next_token = True
                
    def reduce(self, token, rule_no):
        rule = self.grammar[rule_no]
        to_reduce_nt = rule[0]
        rule_rhs = rule[2:]
        curr_node = at.Node(to_reduce_nt)
        to_reduce_count = len(rule_rhs) if rule_rhs[0] != "epsilon" else 0 
        nodes = [] if rule_rhs[0] != "epsilon" else [at.Node("epsilon")]
        for _ in range(to_reduce_count):
            self.stack.pop()
            self.stack.pop()
            nodes.append(self.tree_stack.pop())
        for item in reversed(nodes):
            item.parent = curr_node
        self.tree_stack.append(curr_node)
        
        self.stack.append(to_reduce_nt)        
        self.stack.append(self.where_to_goto(self.parse_table[self.stack[-2]].get(to_reduce_nt)))
        self.to_get_next_token = False
    
        
    def parse(self):
        if(self.to_get_next_token):
            self.token = self.scanner.get_next_token()
        
        token_terminal = self.token[1]
        if(token_terminal == 'NUM' or token_terminal == 'ID'):
            token_terminal = self.token[1]
        elif(token_terminal == 'white_space'): #ignoring whitespaces here TODO : handle it in scanner
            return True
        else :
            token_terminal = self.token[2]
        
        
        if(self.parse_table[self.stack[-1]].get(token_terminal) != None):
            action = self.process_action_string(self.parse_table[self.stack[-1]].get(token_terminal)) # action: 0-> shift/ reduce, 1-> number
            if(action[0] == "shift"):
                self.shift(token_terminal, action[1])
            elif(action[0] == "reduce"):
                self.reduce(token_terminal, action[1])
            elif(action[0] == "accept"):
                node = self.tree_stack.pop()
                node.parent = self.tree_stack[-1]
                print("ACCEPTED")
                return False
        else: #error
            print("ignored token in error: ", self.token)
        
        return True
        
    def generate_parse_tree(self):
        out = ''
        for pre, fill, node in at.RenderTree(self.tree_stack[-1]):
            out += f"{pre}{node.name}\n"
        return out 

    
    def parse_all(self):
        self.to_get_next_token = True
        while(True):
            if not self.parse():
                break
        print(self.tree_stack)
        with open("pt.txt", "w") as f:
            f.write(self.generate_parse_tree())
        