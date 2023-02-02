# group members: Erfan Mojibi
from Scanner import Scanner
from DFA import dfa
from Parser import Parser, read_json
scanner = Scanner("input.txt", dfa)

terminals, non_terminals, first, follow, grammar, parse_table = read_json("table.json")
parse = Parser(terminals, non_terminals, first, follow, grammar, parse_table, scanner)
parse.parse_all()