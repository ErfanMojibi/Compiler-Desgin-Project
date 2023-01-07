import json as js
from typing import Tuple

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
        self.get_next_token = True
        self.token = ""
        self.errors = []

    @staticmethod
    def process_action_string(action_string: str) -> Tuple[str, str]:
        if action_string.startswith("shift"):
            return "shift", action_string[6:]
        elif action_string.startswith("reduce"):
            return "reduce", action_string[7:]
        elif action_string.startswith("accept"):
            return "accept", ""

    @staticmethod
    def where_to_goto(goto_string: str) -> str:
        return goto_string[5:]

    def shift(self, token_terminal: str, state: str) -> None:
        self.stack.append(token_terminal)
        self.stack.append(state)
        # print("stack after shift:", self.stack)
        self.tree_stack.append(at.Node(f"({self.token[1]}, {self.token[2]})"))
        self.get_next_token = True

    def reduce(self, token, rule_no: str) -> None:
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
        self.get_next_token = False

    def get_next_token_terminal(self):
        if self.get_next_token:
            self.token = self.scanner.get_next_token()

        token_terminal = self.token[1]
        if token_terminal == 'NUM' or token_terminal == 'ID':
            token_terminal = self.token[1]
        else:
            token_terminal = self.token[2]
        return token_terminal

    def parse(self):
        token_terminal = self.get_next_token_terminal()
        if token_terminal == 'white_space' or token_terminal == 'COMMENT':
            # ignoring whitespaces and comments here TODO : handle it in scanner
            return True

        if self.parse_table[self.stack[-1]].get(token_terminal) is not None:  # parsing
            action = self.process_action_string(
                self.parse_table[self.stack[-1]].get(token_terminal))  # action: 0-> shift/ reduce, 1-> number
            if action[0] == "shift":
                self.shift(token_terminal, action[1])
            elif action[0] == "reduce":
                self.reduce(token_terminal, action[1])
            elif action[0] == "accept":
                node = self.tree_stack.pop()
                node.parent = self.tree_stack[-1]
                print("ACCEPTED")
                return False
        else:  # error handling
            self.get_next_token = True
            line_number = self.token[0]
            self.errors.append(f"#{line_number} : syntax error, illegal {token_terminal}")
            while True:
                to_break = False
                state = self.stack[-1]
                goto = self.has_goto(state)
                if goto[0]:
                    to_break = True
                    token_terminal = self.get_next_token_terminal()
                    nt_with_goto = goto[1]
                    goto_dest = self.where_to_goto(goto[2])
                    while True:
                        if token_terminal in self.follow[nt_with_goto]:
                            self.stack.append(nt_with_goto)
                            self.stack.append(goto_dest)
                            self.get_next_token = False
                            self.errors.append(f"{line_number} : syntax error, missing {nt_with_goto}")

                        else:
                            self.errors.append(f"#{self.token[0]} : syntax error, discarded ({self.token[1]},"
                                               f" {self.token[2]}) from input")
                            token_terminal = self.get_next_token_terminal()
                if to_break:
                    break
                self.stack.pop()
                forgotten_t_or_nt = self.stack[-1]
                self.errors.append(f"syntax error, discarded {forgotten_t_or_nt} from stack")
                self.stack.pop()

            print("ignored token in error: ", self.token)

        return True

    def has_goto(self, state) -> Tuple[bool, str, str]:
        for key in sorted(self.parse_table[state]):
            if self.parse_table[key].startswith("goto"):
                value = self.parse_table[key]
                return True, key, value
        return False, "", ""

    def generate_parse_tree(self):
        out = ''
        for pre, fill, node in at.RenderTree(self.tree_stack[-1]):
            out += f"{pre}{node.name}\n"
        return out

    def parse_all(self):
        self.get_next_token = True
        while True:
            if not self.parse():
                break
        print(self.tree_stack)
        with open("pt.txt", "w") as f:
            f.write(self.generate_parse_tree())
        with open("errors.txt", "w") as f:
            if len(self.errors) == 0:
                f.write("There is no syntax error.")
            else:
                f.write("\n".join(self.errors))
