# group members: Alireza Haqi, Ali Rahmizad, Erfan Mojibi
from Scanner import Scanner
from DFA import dfa
scanner = Scanner("input.txt", dfa)
scanner.get_all_tokens_and_export()