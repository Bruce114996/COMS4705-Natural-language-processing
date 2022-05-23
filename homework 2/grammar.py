"""
COMS W4705 - Natural Language Processing
Homework 2 - Parsing with Context Free Grammars 
Yassine Benajiba
"""

import sys
from collections import defaultdict
from math import fsum

class Pcfg(object): 
    """
    Represent a probabilistic context free grammar. 
    """

    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None 
        self.read_rules(grammar_file)      
 
    def read_rules(self,grammar_file):
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()
                    
     
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False. 
        """
        therhold_mistake=0.0001
        for grammar_keys, grammar_item in grammar.lhs_to_rules.items():
            item_list = grammar.lhs_to_rules[grammar_keys]
            for item in item_list:
                item = item[1]
                if len(item) == 2:
                    if not item[0].upper() == item[0] or not item[1].upper() == item[1]:
                        return ('Not Valid PCFG')
                elif len(item) == 1:
                    if not item[0].lower() == item[0]:
                        return ('Not Valid PCFG')
                else:
                    return ('Not Valid PCFG')
            prob = [item_list[i][2] for i in range(len(item_list))]
            if abs(fsum(prob) - 1) >= therhold_mistake:
                return ('Not Valid PCFG')
        return ("Valid PCFG")


if __name__ == "__main__":
    with open('atis3.pcfg','r') as grammar_file:
        grammar = Pcfg(grammar_file)
        print(grammar.verify_grammar())#'Valid PCFG'

