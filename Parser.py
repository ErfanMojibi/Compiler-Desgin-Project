import json as js
from typing import Tuple, Any
from CodeGen import CodeGenerator
import anytree as at


def read_json(file_name):
    with open(file_name) as f:
        read_dict = js.load(f)
        return [item[1] for item in read_dict.items()]


class Parser:
    def __init__(self, terminals, non_terminals, first, follow, grammar, parse_table, scanner):
        self.report_parse_tree = True
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.first = first
        self.follow = follow
        self.grammar = grammar
        self.parse_table = parse_table
        self.scanner = scanner
        self.stack = ["0"]  # contains terminals or non-terminals only
        self.complete_token_stack = ["0"]  # contains terminals or tokens
        self.tree_stack = []
        self.get_next_token = True
        self.token = ""
        self.errors = []
        self.code_gen = CodeGenerator(self.scanner.symbol_table, self.grammar)

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

        self.complete_token_stack.append(self.token)
        self.complete_token_stack.append(state)
        # print("stack after shift:", self.stack)
        if token_terminal != "$":
            self.tree_stack.append(at.Node(f"({self.token[1]}, {self.token[2]})"))
        else:
            self.tree_stack.append(at.Node("$"))
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

            self.complete_token_stack.pop()
            self.complete_token_stack.pop()

            nodes.append(self.tree_stack.pop())

        for item in reversed(nodes):
            item.parent = curr_node
        self.tree_stack.append(curr_node)

        self.stack.append(to_reduce_nt)
        self.stack.append(self.where_to_goto(self.parse_table[self.stack[-2]].get(to_reduce_nt)))

        self.code_gen.generate_code(self.token, rule_no)

        self.complete_token_stack.append(to_reduce_nt)
        self.complete_token_stack.append(
            self.where_to_goto(self.parse_table[self.complete_token_stack[-2]].get(to_reduce_nt)))

        self.get_next_token = False

    def get_next_token_terminal(self):
        if self.get_next_token:
            self.token = self.scanner.get_next_token()
        while True:
            if self.token is None:
                self.token = self.scanner.get_next_token()
                continue
            token_terminal = self.token[1]
            if token_terminal == 'NUM' or token_terminal == 'ID' or token_terminal == 'COMMENT' \
                    or token_terminal == 'white_space':
                token_terminal = self.token[1]
            else:
                token_terminal = self.token[2]
            if token_terminal == 'white_space' or token_terminal == 'COMMENT':
                # ignoring whitespaces and comments here TODO : handle it in scanner
                self.token = self.scanner.get_next_token()
                continue
            return token_terminal

    def parse(self):
        token_terminal = self.get_next_token_terminal()
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
                return False
        else:  # error handling
            # skip current token
            line_number = self.token[0]
            self.errors.append(f"#{line_number} : syntax error , illegal {self.token[2]}")
            self.get_next_token = True
            token_terminal = self.get_next_token_terminal()
            self.get_next_token = False

            line_number = self.token[0]

            while True:
                to_break = False
                state = self.stack[-1]
                goto = self.has_goto(state, token_terminal)
                # print(goto)
                if goto[0]:
                    while True:
                        nt_to_handle = self.get_valid_nt_to_handle_error(goto[1], token_terminal)
                        if nt_to_handle is not None:
                            self.stack.append(nt_to_handle)
                            self.stack.append(self.where_to_goto(goto[1][nt_to_handle]))

                            self.complete_token_stack.append(nt_to_handle)
                            self.complete_token_stack.append(self.where_to_goto(goto[1][nt_to_handle]))

                            self.tree_stack.append(at.Node(nt_to_handle))

                            self.errors.append(f"#{line_number} : syntax error , missing {nt_to_handle}")
                            to_break = True
                            self.get_next_token = False
                            # print(self.stack, self.token)
                            break

                        else:
                            if token_terminal == "$":
                                self.errors.append(f"#{line_number} : syntax error , Unexpected EOF")
                                self.report_parse_tree = False
                                return False
                            else:
                                self.errors.append(
                                    f"#{line_number} : syntax error , discarded {self.token[2]} from input")
                                self.get_next_token = True
                                token_terminal = self.get_next_token_terminal()
                                line_number = self.token[0]

                else:
                    self.stack.pop()
                    self.complete_token_stack.pop()

                    forgotten_t_or_nt = self.complete_token_stack[-1]
                    if forgotten_t_or_nt in self.non_terminals:
                        self.errors.append(f"syntax error , discarded {forgotten_t_or_nt} from stack")
                    else:
                        self.errors.append(
                            f"syntax error , discarded ({forgotten_t_or_nt[1]}, {forgotten_t_or_nt[2]}) from stack")
                    self.stack.pop()
                    self.tree_stack.pop()
                    self.complete_token_stack.pop()
                if to_break:
                    break
        return True

    def has_goto(self, state, token_terminal) -> Tuple[bool, Any]:
        for key in self.parse_table[state]:
            if self.parse_table[state][key].startswith("goto"):
                return True, dict(filter(lambda x: x[1].startswith("goto"), self.parse_table[state].items()))
        return False, None

    def get_valid_nt_to_handle_error(self, table_row, token_terminal):
        for item in sorted(table_row):
            if token_terminal in self.follow[item]:
                return item
        return None

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
        print(self.code_gen.export_PB())
        print(self.scanner.symbol_table.table)

        with open("parse_tree.txt", "w") as f:
            if self.report_parse_tree:
                f.write(self.generate_parse_tree())
            else:
                f.write("")
        with open("syntax_errors.txt", "w") as f:
            if len(self.errors) == 0:
                f.write("There is no syntax error.")
            else:
                f.write("\n".join(self.errors))
